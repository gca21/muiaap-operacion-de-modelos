"""Autenticación por API key y autorización por scopes.

- Autenticación (401): ¿quién llama? La clave de `X-API-Key` debe coincidir con
  la de algún cliente configurado.
- Autorización (403): ¿qué puede hacer? El cliente debe tener el scope que
  exige el router.

La clave nunca se devuelve ni se registra en los logs.
"""

import logging
import secrets  # noqa: F401 - pista para S10.2e
from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated

from fastapi import Security
from fastapi.security import APIKeyHeader  # noqa: F401 - pista para S10.2d

from wine_api.dependencies import RequestIdDep, SettingsDep
from wine_api.errors import AuthenticationError, PermissionDeniedError
from wine_api.settings import Scope

logger = logging.getLogger("wine_api.security")

API_KEY_HEADER = "X-API-Key"

api_key_header = APIKeyHeader(
    name=API_KEY_HEADER,
    auto_error=False,
    description="API key del cliente, configurada en WINE_API_CLIENTS.",
)


@dataclass(frozen=True)
class AuthenticatedClient:
    """Cliente ya autenticado. No guarda la clave: no la necesita nadie más."""

    name: str
    scopes: frozenset[str]
    rate_limit_per_minute: int


def authenticate_client(
    settings: SettingsDep,
    request_id: RequestIdDep,
    api_key: Annotated[str | None, Security(api_key_header)],
) -> AuthenticatedClient:
    """Identifica al cliente por su API key o lanza `AuthenticationError`."""

    if api_key is not None:
        try:
            candidate = api_key.encode("ascii")
        except UnicodeEncodeError:
            candidate = None

        if candidate is not None:
            for name, config in settings.clients.items():
                configured_key = config.key.get_secret_value().encode("utf-8")
                if secrets.compare_digest(candidate, configured_key):
                    return AuthenticatedClient(
                        name=name,
                        scopes=frozenset(config.scopes),
                        rate_limit_per_minute=config.rate_limit_per_minute,
                    )

    logger.warning("Rejected API key", extra={"request_id": request_id})
    raise AuthenticationError()


ClientDep = Annotated[AuthenticatedClient, Security(authenticate_client)]


def require_scope(scope: Scope) -> Callable[..., AuthenticatedClient]:
    """Crea una dependencia que exige `scope`; se declara en el `APIRouter`."""

    def check_scope(client: ClientDep) -> AuthenticatedClient:
        if scope not in client.scopes:
            raise PermissionDeniedError()
        return client

    return check_scope
