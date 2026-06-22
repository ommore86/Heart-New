"""GET /health — liveness and readiness check."""

from __future__ import annotations

from fastapi import APIRouter

from backend.model_loader import model_service
from backend.schemas import HealthResponse

router = APIRouter(tags=["System"])


@router.get("/health", response_model=HealthResponse, summary="Liveness & readiness check")
async def health_check() -> HealthResponse:
    """
    Returns the service status and whether the model is loaded.

    - **status**: always "ok" if the server is running
    - **model_loaded**: True if the ensemble model is in memory
    """
    return HealthResponse(
        status="ok",
        model_loaded=model_service.is_loaded,
    )
