"""Punto de extensión del CLI de inferencia sobre un bundle."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from model_packaging.artifact import (
    DEFAULT_BUNDLE_PATH,
    infer_wine_quality,
    load_model_bundle,
)
from model_packaging.contracts import WineQualityRequest


def predict_file(
    input_path: Path,
    output_path: Path,
    bundle_path: Path,
) -> int:
    """valida todas las filas y escribe el CSV solo al final."""
    bundle = load_model_bundle(bundle_path)
    df = pd.read_csv(input_path)

    predictions: list[dict[str, str | float]] = []
    for index, row in df.iterrows():
        sample_id = row.get("sample_id", "")
        if not sample_id:
            raise ValueError(f"Fila {index} tiene un sample_id vacío.")

        request = WineQualityRequest.model_validate(row.drop("sample_id").to_dict())
        prediction = infer_wine_quality(bundle, request)
        predictions.append({"sample_id": sample_id, **prediction.model_dump()})

    pd.DataFrame(predictions).to_csv(output_path, index=False)
    return len(predictions)


def parse_args() -> argparse.Namespace:
    """Declara la interfaz del comando público."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--bundle", default=DEFAULT_BUNDLE_PATH, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    raise SystemExit(
        predict_file(
            input_path=arguments.input,
            output_path=arguments.output,
            bundle_path=arguments.bundle,
        )
    )
