from fastapi import APIRouter, HTTPException

from wine_api.dependencies import PredictorDep, RequestIdDep
from wine_api.schemas import HealthResponse, ErrorResponse # noqa: F401 - pista para S9.1d

SERVICE_NAME = "wine-quality-prediction"

class ModelUnavailableError(Exception):
    '''Raised when prediction model is unavailable'''
    
# S9.3a: declara `tags=["health"]` en el router, no en include_router().
router = APIRouter(tags=["health"])


# S9.3b: añade `summary=`, `response_description=` y un docstring que diga
# cuándo usar el endpoint y qué significa un 503. Documenta el 503 con
# `responses={503: {"model": ErrorResponse, "description": ...}}`.
@router.get(
        "/health",
        summary="Check API status",
        response_description="API health status",
        responses={503: {
            "model": ErrorResponse,
            "description": "Service unavailable"
        }}
)
def read_health(predictor: PredictorDep, request_id: RequestIdDep):
    '''Checks wether the API is operational. Use to verify that the service is running and ready to take requests'''

    # S9.2f: sustituye el HTTPException por `ModelUnavailableError`: el
    # dominio no debería saber de HTTP y el manejador produce el sobre común.
    if not predictor.is_ready():
        raise ModelUnavailableError
    
    # S9.1d: declara `-> HealthResponse` y devuelve una instancia.
    response = HealthResponse.model_validate({
        "status": "ok",
        "service": SERVICE_NAME,
        "model_status": "ready",
        "model_version": predictor.model_version,
        "request_id": request_id,
    })
    return response
