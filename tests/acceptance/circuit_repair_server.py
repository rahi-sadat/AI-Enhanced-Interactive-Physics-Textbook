"""Opt-in localhost replay server; never imported by production or unit tests.

Uses the unchanged recorded file, recorded semantic/OCR responses and actual
upload, evidence, readiness and compiler services. No external model calls.
It deliberately rejects any other file instead of reusing its canned evidence.
"""
import asyncio
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from fastapi import FastAPI, UploadFile, HTTPException
from ai.ingestion.UploadService import UploadService
from ai.ingestion.PageIRBuilder import PageIRBuilder
from ai.ingestion.PhysicsCompiler import PhysicsCompiler
from ai.evidence.pipeline import EvidenceExtractionPipeline
from ai.evidence.ocr.mock import MockOCRProvider
from ai.evidence.segmentation import UnavailableSegmentationProvider
from tests.acceptance.circuit_repair_replay import load_recorded, OUT, ROOT

app=FastAPI()

def ingest(data,name,mime):
    import hashlib
    _,recorded,book,tokens=load_recorded()
    if hashlib.sha256(data).hexdigest()!=recorded.sha256:
        raise HTTPException(422,'This offline replay accepts only the unchanged recorded circuit.')
    asset=UploadService(OUT/'uploads',ROOT/'apps/web/public/uploads').ingest(data,name,mime)
    url='/uploads/'+Path(asset.storage_path).name
    page=PageIRBuilder().build(asset,public_url=url)
    book.source_asset_id=asset.id
    grounded=EvidenceExtractionPipeline(ocr_provider=MockOCRProvider(tokens),
        segmentation_provider=UnavailableSegmentationProvider()).extract_and_fuse(asset,page,book)
    compiled=PhysicsCompiler().compile(grounded)
    if compiled.scene:
        compiled.scene['source']['image']=url
        compiled.scene.setdefault('visual',{})['background_url']=url
    return {'success':True,'status':compiled.status,'source_asset':asset.to_dict(),
            'image_url':url,'page_ir':page.to_dict(),'book_ir':grounded.to_dict(),
            'compiler':compiled.to_dict(),'scene':compiled.scene}

@app.post('/api/ingest')
async def upload(file:UploadFile):
    return await asyncio.to_thread(ingest,await file.read(),file.filename,file.content_type)

if __name__=='__main__':
    import uvicorn
    uvicorn.run(app,host='127.0.0.1',port=8000)
