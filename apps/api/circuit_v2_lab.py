"""Explicit local-only experiment; normal ingestion readiness stays authoritative."""
import asyncio
from fastapi import APIRouter, File, HTTPException, UploadFile
from ai.ingestion.UploadService import UploadValidationError
from ai.perception.circuits.v2_experiment import run_experiment


def create_router(get_services):
    router = APIRouter()

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
            return await asyncio.to_thread(run_experiment, b"".join(chunks), file.filename or "upload",
                                           file.content_type or "application/octet-stream", services)
        except UploadValidationError as error:
            raise HTTPException(422, str(error)) from error

    return router
