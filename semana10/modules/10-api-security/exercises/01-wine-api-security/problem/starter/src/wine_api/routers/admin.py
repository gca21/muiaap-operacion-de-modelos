from fastapi import APIRouter, Depends

from wine_api.dependencies import RequestIdDep, SettingsDep
from wine_api.rate_limit import RateLimiterDep
from wine_api.schemas import ClientUsage, ErrorResponse, UsageResponse
from wine_api.security import require_scope

router = APIRouter(
    prefix="/v1/admin",
    tags=["admin"],
    dependencies=[Depends(require_scope("admin"))],
    responses={
        401: {"model": ErrorResponse, "description": "API key ausente o inválida."},
        403: {"model": ErrorResponse, "description": "El cliente no tiene permiso."},
    },
)


@router.get(
    "/usage",
    summary="Consultar el consumo de los clientes",
    response_description="Peticiones contadas por cliente en la ventana actual.",
)
def get_usage(
    settings: SettingsDep, limiter: RateLimiterDep, request_id: RequestIdDep
) -> UsageResponse:
    """Devuelve el uso y la cuota de cada cliente, sin exponer sus claves."""

    return UsageResponse(
        clients=[
            ClientUsage(
                client=name,
                requests_in_window=limiter.usage(name),
                limit=config.rate_limit_per_minute,
            )
            for name, config in sorted(settings.clients.items())
        ],
        request_id=request_id,
    )
