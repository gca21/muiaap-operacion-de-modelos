"""TODO: carga del .joblib e inferencia sobre características preparadas."""

# Declara DEFAULT_MODEL_PATH, load_wine_quality_model() e infer_wine_quality().
# Comprueba las características del artefacto antes de llamar al clasificador.

import pathlib
from collections.abc import Mapping, Sequence
from typing import Protocol

import joblib

from .preprocess import FEATURE_NAMES, WineFeatures

relative_path = "models/wine_quality_classifier 3.joblib"
DEFAULT_MODEL_PATH = (
    pathlib.Path(__file__).parent.parent.parent.joinpath(relative_path).resolve()
)


class WineQualityModel(Protocol):
    def predict(self, features: list[list[float]]) -> Sequence[str]: ...

    def predict_proba(
        self, features: list[list[float]]
    ) -> Sequence[Sequence[float]]: ...


def load_wine_quality_model(path: pathlib.Path):
    if not path.is_file():
        raise FileNotFoundError(f"El fichero {path} no se encontró.")

    payload = joblib.load(path)

    if not isinstance(payload, Mapping):
        raise ValueError("El artefacto debe contener metadatos y un estimador")

    estimator = payload.get("estimator")
    model_version = payload.get("model_version")
    feature_names = payload.get("feature_names")

    if feature_names != list(FEATURE_NAMES):
        raise ValueError("Los feature_names del modelo no coinciden con el contrato.")

    if estimator is None:
        raise ValueError("El artefacto no contiene un clasificador compatible.")

    if model_version is None:
        raise ValueError("El artefacto no contiene model_version.")

    if feature_names is None:
        raise ValueError("El artefacto no contiene feature_names.")

    if not hasattr(estimator, "predict") or not hasattr(estimator, "predict_proba"):
        raise ValueError("El artefacto no contiene un clasificador compatible.")

    return payload


def infer_wine_quality(
    model: WineQualityModel, features: WineFeatures
) -> tuple[str, float]:

    feature_vector = [features.as_vector()]
    prediction = model.predict(feature_vector)[0]
    confidence = max(model.predict_proba(feature_vector)[0])
    return (prediction, confidence)
