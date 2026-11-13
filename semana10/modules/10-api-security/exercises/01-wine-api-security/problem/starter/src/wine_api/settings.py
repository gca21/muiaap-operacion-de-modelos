"""Configuración y secretos del servicio, leídos del entorno o de `.env`.

Todas las variables llevan el prefijo `WINE_API_`. Como ejemplo ya está migrada
`WINE_API_MODE`, que en S9 se leía con `os.environ`. Los tipos complejos
(`WINE_API_CLIENTS`, `WINE_API_CORS_ORIGINS`) se escribirán en JSON.
"""

from typing import Literal

from pydantic import (  # noqa: F401 - pistas para S10.1
    BaseModel,
    Field,
    SecretStr,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

Scope = Literal["predict", "admin"]


class ClientConfig(BaseModel):
    """Credencial, permisos y cuota de un cliente de la API."""

    key: SecretStr
    scopes: list[Scope]
    rate_limit_per_minute: int = Field(default=60, gt=0)


class Settings(BaseSettings):
    """Configuración validada al arrancar: si algo es inválido, no arranca."""

    model_config = SettingsConfigDict(
        env_prefix="WINE_API_", env_file=".env", extra="ignore"
    )

    mode: Literal["ready", "unavailable"] = "ready"
    clients: dict[str, ClientConfig] = Field(default_factory=dict)
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:8501"])
    docs_enabled: bool = True

    @field_validator("cors_origins")
    @classmethod
    def reject_wildcard_cors_origin(cls, origins: list[str]) -> list[str]:
        if "*" in origins:
            raise ValueError("CORS origins must be listed explicitly")
        return origins
