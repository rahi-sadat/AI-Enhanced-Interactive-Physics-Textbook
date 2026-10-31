"""Verify trace/report integrity without network or physics execution."""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote
import cv2
import numpy as np
from build_pipeline_trace_report import ROOT,RAW,OUT,read,dump

def main():
    secrets=[]
    env=ROOT/'.env'
    if env.exists():
        for line in env.read_text(encoding='utf-8').splitlines():
            if re.match(r'\s*(GEMINI_API_KEY|GOOGLE_API_KEY)\s*=',line):
                v=line.split('=',1)[1].strip().strip('"\'')
                if v:secrets.append(v.encode())
    results=[]
    for r in read(OUT/'summary.json'):
        f=RAW/r['trace_id'];errors=[];missing=[];leaks=[]
        jpg=(f/'00_source/original.jpg').read_bytes()
        jpg_image=cv2.imdecode(np.frombuffer(jpg,np.uint8),cv2.IMREAD_COLOR)
        png=cv2.imread(str(f/'00_source/original.png'))
        pixel_equal=np.array_equal(jpg_image,png)
        if not pixel_equal:errors.append('Source PNG pixels differ from JPEG decode')
        if not all(r['identity'][k] for k in ('upload_byte_identity','SDK_image_byte_identity')):errors.append('Source identity failed')
        nhtml=0
        for p in f.rglob('*'):
            if not p.is_file() or p.suffix not in ('.json','.html','.txt','.md'):continue
            data=p.read_bytes()
            if any(s in data for s in secrets):leaks.append(str(p.relative_to(f)))
            if p.suffix=='.html':
                nhtml+=1
                for ref in re.findall(r'(?:href|src)="([^"]+)"',data.decode('utf-8')):
                    if '://' in ref or ref.startswith(('data:','#')):continue
                    if not (p.parent/unquote(ref.split('#')[0])).exists():missing.append({'page':str(p.relative_to(f)),'target':ref})
        if r['state']=='SIMULATING' and not (f/'14_renderer/runtime_t0_overlay.png').exists():errors.append('Missing t=0 overlay')
        calls=list((f/'calls').iterdir())
        incomplete=[p.name for p in calls if not all((p/name).exists() for name in ('actual_input.json','actual_output.json','locals_after.json','location.json','STAGE.html'))]
        # Import-time class serialization gaps are disclosed; list exactly, never call them complete.
        results.append({'trace_id':f.name,'source_pixel_equal':pixel_equal,'original_sha256':hashlib.sha256(jpg).hexdigest(),'HTML_pages':nhtml,'missing_links':missing,'credential_leak_paths':leaks,'incomplete_call_snapshots':incomplete,'errors':errors})
    dump(OUT/'artifact_verification.json',results)
    print(json.dumps(results,indent=2))
    if any(r['errors'] or r['missing_links'] or r['credential_leak_paths'] for r in results):raise SystemExit(1)

if __name__=='__main__':main()
