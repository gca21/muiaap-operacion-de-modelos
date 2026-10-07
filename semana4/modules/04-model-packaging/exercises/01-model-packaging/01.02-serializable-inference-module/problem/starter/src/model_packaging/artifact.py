"""Puntos de extensión del taller de serialización."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, field_validator

from model_packaging.contracts import (
    QualityBand,
    WineQualityPrediction,
    WineQualityRequest,
)

from model_packaging.preprocess import PREPROCESSING_VERSION, FEATURE_NAMES
import json
import joblib

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
            raise ValueError(f"schema_version incompatible, valor esperado: {ARTIFACT_SCHEMA_VERSION}")
        return value

    @field_validator("model_version")
    @classmethod
    def validate_model_version(cls, value: str) -> str:
        if len(value.strip()) == 0:
            raise ValueError(f"La versión del modelo debe contener algún valor")
        return value

    @field_validator("preprocessing_version")
    @classmethod
    def validate_preprocessing_version(cls, value: str) -> str:
        if value != PREPROCESSING_VERSION:
            raise ValueError(f"preprocessing_version incompatible, valor esperado: {PREPROCESSING_VERSION}")
        return value

    @field_validator("feature_names")
    @classmethod
    def validate_feature_names(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if value != FEATURE_NAMES:
            raise ValueError("feature_names no coincide con el orden del contrato")
        return value

    @field_validator("output_labels")
    @classmethod
    def validate_output_labels(cls, value: tuple[QualityBand, ...]) -> tuple[QualityBand, ...]:
        if value != OUTPUT_LABELS:
            raise ValueError(f"output_labels no coincide con el contrato")


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
        estimator_type=type(estimator).__name__
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
    with open(bundle_path / "manifest.json", "w") as f:
        f.write(manifest.model_dump_json(indent=4))

    joblib.dump(estimator, bundle_path / "model.joblib")

    return manifest


def load_model_bundle(bundle_path: Path) -> LoadedModelBundle:
    """TODO: valida el manifiesto antes de cargar el estimador."""

    raise NotImplementedError("Implementa load_model_bundle().")


def infer_wine_quality(
    bundle: LoadedModelBundle,
    request: WineQualityRequest,
) -> WineQualityPrediction:
    """TODO: preprocesa, invoca el estimador y valida la respuesta."""

    raise NotImplementedError("Implementa infer_wine_quality().")
