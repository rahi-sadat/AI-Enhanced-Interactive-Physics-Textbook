"""Opt-in local real-image pipeline audit; never used by offline test suites."""
import argparse
from collections import Counter
import hashlib
import json
import mimetypes
from pathlib import Path
import time
import zipfile
import httpx


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--api", default="http://127.0.0.1:8001")
    parser.add_argument("--output", type=Path, default=Path("outputs/circuit_v2_pipeline_99"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output/"images").mkdir(exist_ok=True)
    (args.output/"results").mkdir(exist_ok=True)
    summary = []
    with zipfile.ZipFile(args.archive) as archive, httpx.Client(timeout=240,trust_env=False) as client:
        images = sorted((n for n in archive.namelist() if Path(n).suffix.lower() in
                         {".png",".jpg",".jpeg",".webp"}),key=str.casefold)
        for i,name in enumerate(images,1):
            filename = Path(name).name
            data = archive.read(name)
            (args.output/"images"/filename).write_bytes(data)
            result_path = args.output/"results"/f"{i:03}.json"
            start = time.perf_counter()
            if result_path.exists():
                result = json.loads(result_path.read_text(encoding="utf-8"))
            else:
                try:
                    response = client.post(args.api+"/api/experiments/circuit-v2",
                        files={"file":(filename,data,mimetypes.guess_type(filename)[0] or "image/png")})
                    response.raise_for_status()
                    result = response.json()
                except Exception as error:
                    result = {"request_error":str(error)}
                result.update(filename=filename,sha256=hashlib.sha256(data).hexdigest())
                result_path.write_text(json.dumps(result,indent=2),encoding="utf-8")
            row = {"index":i,"filename":filename,"detections":len(result.get("detections",[])),
                   "compiler":result.get("compiler",{}).get("status"),
                   "first_blocker":result.get("first_blocker"),
                   "preview":bool(result.get("preview_scene")),"error":result.get("request_error"),
                   "wall_seconds":round(time.perf_counter()-start,2)}
            summary.append(row)
            (args.output/"progress.json").write_text(json.dumps({"done":i,"total":len(images),"last":row},indent=2))
            print(i,len(images),filename,row["compiler"],row["preview"],flush=True)
    totals = {"images":len(summary),"compiler_status":dict(Counter(r["compiler"] for r in summary)),
              "previews":sum(r["preview"] for r in summary),"request_errors":sum(bool(r["error"]) for r in summary),
              "first_blockers":dict(Counter(r["first_blocker"]["stage"] for r in summary if r["first_blocker"]))}
    (args.output/"summary.json").write_text(json.dumps({"totals":totals,"images":summary},indent=2),encoding="utf-8")
    print(json.dumps(totals),flush=True)


if __name__ == "__main__":
    main()
