"""Explicit local-only experiment; normal ingestion readiness stays authoritative."""
import asyncio
from collections import OrderedDict
from copy import deepcopy
from typing import Literal
from uuid import uuid4
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, ConfigDict, Field
from ai.ingestion.UploadService import UploadValidationError
from ai.perception.circuits.v2_experiment import run_experiment
from ai.perception.circuits.fault_analysis import analyze_book_circuit
from shared.schemas.ingestion import BookIR


class CircuitAnalysisRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    analysis_id: str
    mode: Literal['ideal','qualitative','non_ideal'] = 'ideal'
    source_internal_resistance_ohm: float | None = Field(None, strict=True, ge=0, allow_inf_nan=False)
    short_path_resistance_ohm: float | None = Field(None, strict=True, gt=0, allow_inf_nan=False)
    fault_path_id: str | None = None


class CircuitValueCorrection(BaseModel):
    model_config = ConfigDict(extra='forbid')
    analysis_id: str
    component_id: str
    value: float = Field(strict=True,allow_inf_nan=False)
    unit: str


def create_router(get_services):
    router = APIRouter()
    # Browser inputs identify a server-extracted graph, never a client-supplied
    # replacement BookIR. Bounded session cache; all heavy work stays off-loop.
    analyses = OrderedDict()

    @router.post("/api/experiments/circuit-v2")
    async def circuit_v2_experiment(file: UploadFile = File(...)):
        chunks, size = [], 0
        while chunk := await file.read(65536):
            size += len(chunk)
            if size > 50*1024*1024:
                raise HTTPException(422, "Image exceeds 50 MB.")
            chunks.append(chunk)
        try:
            services = await asyncio.to_thread(get_services)
            result = await asyncio.to_thread(run_experiment, b"".join(chunks), file.filename or "upload",
                                             file.content_type or "application/octet-stream", services)
            if result.get('book_ir'):
                token = uuid4().hex
                analyses[token] = deepcopy(result['book_ir'])
                while len(analyses)>32:analyses.popitem(last=False)
                result['analysis_id'] = token
            return result
        except UploadValidationError as error:
            raise HTTPException(422, str(error)) from error

    @router.post('/api/experiments/circuit-v2/analysis')
    async def circuit_analysis(request: CircuitAnalysisRequest):
        original = analyses.get(request.analysis_id)
        if original is None:
            raise HTTPException(404, 'Analysis expired or unknown. Upload the original image again.')
        arguments = request.model_dump(exclude={'analysis_id'})
        book = BookIR.from_dict(deepcopy(original))
        return await asyncio.to_thread(analyze_book_circuit, book, **arguments)

    @router.post('/api/experiments/circuit-v2/correct-value')
    async def correct_value(request: CircuitValueCorrection):
        original=analyses.get(request.analysis_id)
        if original is None:
            raise HTTPException(404,'Analysis expired or unknown. Upload the original image again.')
        def correct():
            from ai.resolution.engine import ResolutionEngine
            from ai.ingestion.PhysicsCompiler import PhysicsCompiler
            book=BookIR.from_dict(deepcopy(original))
            resolution=ResolutionEngine.apply_resolution(book,dict(
                parameter_name=f'component.{request.component_id}.value',resolved_value=request.value,
                canonical_unit=request.unit,resolution_source='user_corrected',user_accepted=True,
                notes='Explicit correction in circuit inspection; original OCR evidence is preserved.'))
            if not resolution.success:
                raise HTTPException(422,resolution.error)
            compiled=PhysicsCompiler().compile(book)
            return dict(book_ir=book.to_dict(),scene=compiled.scene,
                compiler=dict(status=compiled.status,issues=compiled.issues),
                ideal_analysis=analyze_book_circuit(book,mode='ideal'),
                fault_analysis=analyze_book_circuit(book,mode='qualitative'))
        result=await asyncio.to_thread(correct)
        token=uuid4().hex
        analyses[token]=deepcopy(result['book_ir'])
        while len(analyses)>32:analyses.popitem(last=False)
        result.update(analysis_id=token,parent_analysis_id=request.analysis_id)
        return result

    return router
