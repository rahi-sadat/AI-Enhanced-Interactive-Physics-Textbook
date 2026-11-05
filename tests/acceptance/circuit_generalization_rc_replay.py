"""Prepare an explicitly synthetic, offline OCR/semantic replay for browser RC checks.

Actual CV, grounding and compilation run; this is not live provider evidence.
The numerical and geometric annotations originate in the unit-test drawing.
"""
import json
import runpy
import sys
from pathlib import Path
import cv2

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
OUT=ROOT/'storage/generated/circuit_generalization_live'

def main():
    definitions=runpy.run_path(str(ROOT/'tests/unit/test_circuit_capacitor_pipeline.py'))
    image,book,_=definitions['grounded_rc']()
    OUT.mkdir(parents=True,exist_ok=True)
    filename=OUT/'rc_synthetic_replay.png'
    cv2.imwrite(str(filename),image)
    payload={'success':True,'status':'needs-review','domain':'circuits','scenario':'dc_linear',
        'image_url':'/@fs/'+filename.as_posix(),'book_ir':book.to_dict(),'scene':None,
        'width':image.shape[1],'height':image.shape[0],
        'test_mode':'Synthetic drawing, annotated offline OCR and semantic inputs; actual CV/grounding'}
    (OUT/'rc_synthetic_replay_ingest.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__': main()
