"""Puntos de extensión del taller de serialización."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import joblib
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from model_packaging.contracts import (
    QualityBand,
    WineQualityPrediction,
    WineQualityRequest,
)
from model_packaging.preprocess import (
    FEATURE_NAMES,
    PREPROCESSING_VERSION,
    preprocess_wine_request,
)

ARTIFACT_SCHEMA_VERSION = "wine-quality-bundle-v1"
DEFAULT_BUNDLE_PATH = Path("models/wine_quality_bundle")
MANIFEST_FILENAME = "manifest.json"
MODEL_FILENAME = "model.joblib"
OUTPUT_LABELS: tuple[QualityBand, ...] = (
    "needs_review",
    "acceptable",
    "excellent",
)


class WineQualityEstimator(Protocol):
    """Interfaz mínima que debe cumplir el estimador cargado."""

    def predict(self, features: list[list[float]]) -> Sequence[str]:
        """Devuelve una etiqueta por fila."""

    def predict_proba(self, features: list[list[float]]) -> Sequence[Sequence[float]]:
        """Devuelve probabilidades por fila."""


class ArtifactManifest(BaseModel):
    """Declara y valida los metadatos del bundle."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str
    model_version: str = Field(min_length=1)
    preprocessing_version: str
    feature_names: tuple[str, ...]
    output_labels: tuple[QualityBand, ...]
    estimator_type: str = Field(min_length=1)

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, value: str) -> str:
        if value != ARTIFACT_SCHEMA_VERSION:
            raise ValueError(
                f"schema_version incompatible, "
                f"valor esperado: {ARTIFACT_SCHEMA_VERSION}"
            )
        return value

    @field_validator("model_version")
    @classmethod
    def validate_model_version(cls, value: str) -> str:
        if len(value.strip()) == 0:
            raise ValueError("La versión del modelo debe contener algún valor")
        return value

    @field_validator("preprocessing_version")
    @classmethod
    def validate_preprocessing_version(cls, value: str) -> str:
        if value != PREPROCESSING_VERSION:
            raise ValueError(
                f"preprocessing_version incompatible, "
                f"valor esperado: {PREPROCESSING_VERSION}"
            )
        return value

    @field_validator("feature_names")
    @classmethod
    def validate_feature_names(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if value != FEATURE_NAMES:
            raise ValueError("feature_names no coincide con el orden del contrato")
        return value

    @field_validator("output_labels")
    @classmethod
    def validate_output_labels(
        cls, value: tuple[QualityBand, ...]
    ) -> tuple[QualityBand, ...]:
        if value != OUTPUT_LABELS:
            raise ValueError("output_labels no coincide con el contrato")
        return value


@dataclass(frozen=True)
class LoadedModelBundle:
    """Bundle cargado; no modificar esta interfaz pública."""

    estimator: WineQualityEstimator
    manifest: ArtifactManifest


def create_manifest(
    estimator: WineQualityEstimator, model_version: str
) -> ArtifactManifest:
    return ArtifactManifest(
        schema_version=ARTIFACT_SCHEMA_VERSION,
        model_version=model_version,
        preprocessing_version=PREPROCESSING_VERSION,
        feature_names=FEATURE_NAMES,
        output_labels=OUTPUT_LABELS,
        estimator_type=type(estimator).__name__,
    )


def save_model_bundle(
    bundle_path: Path,
    estimator: WineQualityEstimator,
    manifest: ArtifactManifest | None = None,
) -> ArtifactManifest:
    """Escribe manifest.json y model.joblib de forma segura."""

    if manifest is None:
        raise ValueError("El manifest no debe estar vacío")

    bundle_path.mkdir(parents=True, exist_ok=True)
    with open(bundle_path / MANIFEST_FILENAME, "w") as f:
        f.write(manifest.model_dump_json(indent=4))

    joblib.dump({"estimator": estimator}, bundle_path / MODEL_FILENAME)

    return manifest


def load_model_bundle(bundle_path: Path) -> LoadedModelBundle:
    """valida el manifiesto antes de cargar el estimador."""

    manifest_path = bundle_path / MANIFEST_FILENAME
    model_path = bundle_path / MODEL_FILENAME
    if not manifest_path.is_file() or not model_path.is_file():
        raise FileNotFoundError(
            f"El bundle debe contener {MANIFEST_FILENAME} y {MODEL_FILENAME}: "
            f"{bundle_path}"
        )

    try:
        manifest = ArtifactManifest.model_validate_json(
            manifest_path.read_text(encoding="utf-8")
        )
    except (OSError, ValidationError, ValueError) as error:
        raise ValueError(f"manifest.json inválido: {error}") from error

    payload = joblib.load(model_path)
    if not isinstance(payload, Mapping):
        raise ValueError("model.joblib debe contener un mapa con estimator.")
    estimator = payload.get("estimator")
    return LoadedModelBundle(
        estimator=estimator,
        manifest=manifest,
    )


def infer_wine_quality(
    bundle: LoadedModelBundle,
    request: WineQualityRequest,
) -> WineQualityPrediction:
    """preprocesa, invoca el estimador y valida la respuesta."""
    features = preprocess_wine_request(request)
    rows = [features.as_vector()]

    predicted_labels = bundle.estimator.predict(rows)
    probabilities = bundle.estimator.predict_proba(rows)
    probability_row = probabilities[0]

    try:
        return WineQualityPrediction(
            quality_band=str(predicted_labels[0]),
            confidence=max(probability_row),
            model_version=bundle.manifest.model_version,
            preprocessing_version=bundle.manifest.preprocessing_version,
        )
    except (ValidationError, ValueError) as e:
        raise ValueError(f"La salida del modelo no cumple el contrato: {e}") from e
