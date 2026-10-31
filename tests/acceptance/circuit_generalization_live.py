"""Opt-in production API acceptance: sends the supplied fixtures to live providers.

Run separately from offline pytest. The server must already be running.
Responses are retained in ignored storage, including failures; no canned model
response is substituted. Does not install models or start/restart servers.
"""
import json
import os
import sys
from pathlib import Path
import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/"storage/generated/circuit_generalization_live"


def main():
    load_dotenv(ROOT/".env")
    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit("Live acceptance requires GEMINI_API_KEY; offline tests never call providers.")
    OUT.mkdir(parents=True, exist_ok=True)
    with httpx.Client(base_url="http://127.0.0.1:8000", timeout=240) as client:
        client.get("/api/health").raise_for_status()
        paths=[Path(p) for p in sys.argv[1:]] or sorted((ROOT/"tests/fixtures/circuit_generalization").iterdir())
        for path in paths:
            if path.suffix.lower() not in {".jpg",".jpeg",".png"}:
                continue
            print(f"Analyzing {path.name}", flush=True)
            try:
                response=client.post("/api/ingest",files={"file":(path.name,path.read_bytes(),
                    "image/png" if path.suffix==".png" else "image/jpeg")})
                data=response.json()
                (OUT/f"{path.stem}_ingest.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
                book=data.get("book_ir",{})
                print(json.dumps({"image":path.name,"http":response.status_code,
                    "status":data.get("status"),"scene":bool(data.get("scene")),
                    "error":book.get("provenance",{}).get("error"),
                    "issues":data.get("issues"),"geometry":book.get("geometry",{}).get("circuit_validation")},
                    ensure_ascii=False),flush=True)
                if book.get("subtype")!="dc_linear":
                    continue
                review=client.post("/api/resolution/review",json={"book_ir":book}).json()
                (OUT/f"{path.stem}_review.json").write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding="utf-8")
            except Exception as error:
                print(f"{path.name}: {type(error).__name__}: {error}",flush=True)


if __name__=="__main__":
    main()
