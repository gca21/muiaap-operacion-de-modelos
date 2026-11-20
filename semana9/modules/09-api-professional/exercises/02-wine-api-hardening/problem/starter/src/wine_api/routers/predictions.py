from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Body

from wine_api.dependencies import PredictorDep, RequestIdDep
from wine_api.schemas import (
    VALID_FEATURES_EXAMPLE,
    ErrorResponse,
    Prediction,
    PredictionRequest,
    PredictionResponse,
)

# S9.3a: mueve aquí `prefix="/v1/predictions"` y `tags=["predictions"]`.
# S9.3c: declara a nivel de router `responses=` para 400, 422 y 503 con
# `{"model": ErrorResponse, "description": ...}`. Así el 422 deja de
# documentarse como `HTTPValidationError`, que ya no es lo que devolvemos.
router = APIRouter(
    prefix="/v1/predictions",
    tags=["predictions"],
    responses={
        400: {
                "model": ErrorResponse,
                "description": "Bad request. The request contains invalid data."
        },
        422: {
            "model": ErrorResponse,
            "description": "Unprocessable entity. The request data cannot be processed."
        },
        503: {
            "model": ErrorResponse,
            "description": "Service unavailable. The prediction model is not ready."
        },
    }
)


@router.post(
    "",
    summary="Create a wine quality prediction",
    response_description="Wine quality prediction and metadata."
)
def create_prediction(
    payload: Annotated[
        PredictionRequest,
        Body(
            openapi_examples={
                "valid": {
                    "summary": "Valid feature values",
                    "description": "A complete request with valid feature values.",
                    "value": {"features": VALID_FEATURES_EXAMPLE},
                },
                "wrong_type": {
                    "summary": "Invalid feature type",
                    "description": "Alcohol must be a number.",
                    "value": {
                        "features": {
                            **VALID_FEATURES_EXAMPLE,
                            "alcohol": "mucho",
                        }
                    },
                },
                "out_of_range": {
                    "summary": "Feature outside its range",
                    "description": "Alcohol must be between 5 and 20.",
                    "value": {
                        "features": {
                            **VALID_FEATURES_EXAMPLE,
                            "alcohol": 25,
                        }
                    },
                },
            }
        ),
    ],
    predictor: PredictorDep,
    request_id: RequestIdDep,
) -> PredictionResponse:
    '''Request a wine quality prediction from the model'''
    # S9.3e: añade summary, response_description y un docstring útil para
    # quien consume la API (campos, rangos, decimales de confidence).
    # S9.3f: ofrece en Swagger al menos tres ejemplos de cuerpo (uno válido
    # y dos inválidos). Investiga `Annotated[PredictionRequest, Body(...)]` con
    # `openapi_examples=`; usa VALID_FEATURES_EXAMPLE como base.
    output = predictor.predict(payload.features)
    # S9.1e: este dict expone `raw_score` y la confianza sin redondear.
    # Declara `-> PredictionResponse` y construye el modelo; para pasar de la
    # dataclass ModelOutput a Prediction investiga `from_attributes=True`.

    prediction = Prediction.model_validate(output, from_attributes=True)
    response = PredictionResponse.model_validate({
        "prediction": prediction,
        "request_id": request_id,
        "served_at": datetime.now()
    })
    return response
