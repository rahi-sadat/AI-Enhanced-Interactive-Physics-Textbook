"""Opt-in observational recorder for real browser uploads; no mock/fallback data.

Run with PHYSICS_TRACE=1 and configured GEMINI_API_KEY. Outputs are git-ignored.
Uses Python profiling and an ASGI context variable; production files are untouched.
"""
from __future__ import annotations
import contextvars
import dataclasses
import dis
import enum
import hashlib
import inspect
import json
import os
from pathlib import Path
import re
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / '.env')
if os.getenv('PHYSICS_TRACE') != '1' or not os.getenv('GEMINI_API_KEY'):
    raise SystemExit('Requires PHYSICS_TRACE=1 and GEMINI_API_KEY; no substitute provider.')
if os.getenv('USE_MOCK_VISION', '').lower() in ('1', 'true', 'yes'):
    raise SystemExit('Refusing mock provider for real upload trace.')

import numpy as np
import cv2
from apps.api.main import app as real_app

OUT = ROOT / 'storage/generated/debug_traces/20261016'
OUT.mkdir(parents=True, exist_ok=True)
TRACE = contextvars.ContextVar('physics_trace', default=None)
LOCK = threading.Lock()
COUNTERS = {}
FRAMES = {}
SECRET = os.getenv('GEMINI_API_KEY')

def clean(s):
    return s.replace(SECRET, '[REDACTED]') if SECRET else s

def pack(value, folder, seen=None):
    seen = set() if seen is None else seen
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return clean(value)
    if isinstance(value, enum.Enum):
        return pack(value.value, folder, seen)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, (bytes, bytearray)):
        digest = hashlib.sha256(value).hexdigest()
        p = folder / (digest + '.bin')
        if not p.exists(): p.write_bytes(value)
        return {'bytes': len(value), 'sha256': digest, 'artifact': str(p.relative_to(OUT))}
    if isinstance(value, np.ndarray):
        digest = hashlib.sha256(value.tobytes()).hexdigest()
        p = folder / (digest + '.npy')
        if not p.exists(): np.save(p, value)
        result = {'shape': list(value.shape), 'dtype': str(value.dtype), 'artifact': str(p.relative_to(OUT))}
        if value.dtype == np.uint8 and value.ndim in (2, 3) and (value.ndim == 2 or value.shape[-1] in (1,3,4)):
            png = p.with_suffix('.png')
            if not png.exists(): cv2.imwrite(str(png), value)
            result['image'] = str(png.relative_to(OUT))
        if value.size < 50000: result['values'] = value.tolist()
        return result
    if id(value) in seen: return {'type': type(value).__name__, 'reference': 'already serialized'}
    seen.add(id(value))
    if isinstance(value, dict):
        return {str(k): '[REDACTED]' if re.search(r'api.?key|authorization|token_secret', str(k), re.I) else pack(v, folder, seen.copy()) for k,v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [pack(v, folder, seen.copy()) for v in value]
    if dataclasses.is_dataclass(value):
        return {f.name: pack(getattr(value, f.name), folder, seen.copy()) for f in dataclasses.fields(value)}
    if hasattr(value, 'model_dump'):
        return pack(value.model_dump(), folder, seen)
    if hasattr(value, 'to_dict'):
        return pack(value.to_dict(), folder, seen)
    if isinstance(value, BaseException): return {'type': type(value).__name__, 'message': clean(str(value))}
    return {'type': type(value).__module__ + '.' + type(value).__name__, 'not_serialized': True}

def dump(p, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding='utf-8')

def interesting(frame):
    file = frame.f_code.co_filename.replace('\\', '/')
    name = frame.f_code.co_name
    if file.endswith('/google/genai/models.py') and name in ('generate_content', '_generate_content'): return True
    if not file.startswith(str(ROOT).replace('\\','/') + '/'): return False
    rel = file[len(str(ROOT))+1:]
    if not rel.startswith(('ai/','engine/','shared/schemas/','apps/api/')): return False
    if name in ('to_dict','__init__','__post_init__','<listcomp>','<dictcomp>','<genexpr>','<setcomp>'): return False
    return True

def profiler(frame, event, arg):
    tid = TRACE.get()
    if not tid or event not in ('call','return') or not interesting(frame): return
    try:
        key = (threading.get_ident(), id(frame))
        folder = OUT / tid / 'calls'
        arrays = OUT / tid / 'arrays'
        folder.mkdir(parents=True, exist_ok=True)
        arrays.mkdir(exist_ok=True)
        if event == 'call':
            if key in FRAMES: return  # coroutine resumes: retain its original call
            with LOCK:
                seq = COUNTERS.get(tid, 0) + 1
                COUNTERS[tid] = seq
            code = frame.f_code
            name = getattr(code, 'co_qualname', code.co_name)
            p = folder / f'{seq:05d}_{re.sub("[^A-Za-z0-9_.-]", "_", name)}'
            p.mkdir()
            caller = frame.f_back
            meta = {'trace_id': tid, 'sequence': seq, 'status': 'EXECUTED', 'file': code.co_filename, 'function': name, 'line': code.co_firstlineno,
                    'caller': {'file': caller.f_code.co_filename, 'function': caller.f_code.co_name, 'line': caller.f_lineno} if caller else None}
            dump(p / 'location.json', meta)
            dump(p / 'actual_input.json', pack({k:v for k,v in frame.f_locals.items() if k not in ('self','cls')}, arrays))
            try: (p / 'contract_or_schema.txt').write_text(inspect.getsource(code), encoding='utf-8')
            except (OSError, TypeError): pass
            FRAMES[key] = p
        elif key in FRAMES:
            if frame.f_code.co_flags & (inspect.CO_COROUTINE | inspect.CO_GENERATOR):
                if dis.opname[frame.f_code.co_code[frame.f_lasti]] in ('YIELD_VALUE', 'YIELD_FROM'):
                    return  # suspension is not a completed output
            p = FRAMES.pop(key)
            dump(p / 'actual_output.json', pack(arg, arrays))
            dump(p / 'locals_after.json', pack({k:v for k,v in frame.f_locals.items() if k not in ('self','cls','client')}, arrays))
    except Exception as e:
        with (OUT / 'recorder_errors.log').open('a', encoding='utf-8') as f: f.write(clean(str(e)) + '\n')

class TraceApp:
    async def __call__(self, scope, receive, send):
        headers = dict(scope.get('headers', []))
        tid = headers.get(b'x-physics-trace-id', b'').decode()
        if scope['type'] != 'http' or not re.fullmatch(r'TRACE-[A-Z0-9-]+', tid):
            return await real_app(scope, receive, send)
        token = TRACE.set(tid)
        folder = OUT / tid / 'http'
        folder.mkdir(parents=True, exist_ok=True)
        stamp = str(time.time_ns())
        received, sent = [], []
        dump(folder / (stamp + '_request.json'), {'trace_id':tid,'method':scope['method'],'path':scope['path'],'headers':[(k.decode(), '[REDACTED]' if k in (b'authorization',b'cookie') else clean(v.decode())) for k,v in scope['headers']]})
        async def recv():
            msg = await receive()
            if msg.get('body'):
                received.append(msg['body'])
                with (folder / (stamp + '_request_body.bin')).open('ab') as capture:
                    capture.write(msg['body'])
            return msg
        async def transmit(msg):
            if msg.get('body'): sent.append(msg['body'])
            if msg['type'] == 'http.response.start':
                dump(folder / (stamp + '_response_status.json'), {'status':msg['status']})
                msg = dict(msg, headers=list(msg.get('headers', [])) + [(b'x-physics-trace-id', tid.encode())])
            await send(msg)
        try:
            await real_app(scope, recv, transmit)
        finally:
            (folder / (stamp + '_request_body.bin')).write_bytes(b''.join(received))
            (folder / (stamp + '_response_body.json')).write_bytes(b''.join(sent))
            TRACE.reset(token)

if __name__ == '__main__':
    import uvicorn
    sys.setprofile(profiler)
    threading.setprofile(profiler)
    uvicorn.run(TraceApp(), host='0.0.0.0', port=8000, log_level='info')
