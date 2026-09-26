"""TODO: script CLI que encadena contratos, preprocesado e inferencia."""

import argparse
import sys
from pathlib import Path

import pandas as pd

from .contracts import WineQualityPrediction, WineQualityRequest
from .inference import (
    DEFAULT_MODEL_PATH,
    infer_wine_quality,
    load_wine_quality_model,
)
from .preprocess import PREPROCESSING_VERSION, preprocess_wine_request


def predict_file(
    input_path: Path,
    output_path: Path,
    model_path: Path,
) -> int:
    model = load_wine_quality_model(model_path)
    predictions: list[dict[str, str | float]] = []

    df = pd.read_csv(input_path)

    for _idx, row in df.iterrows():
        sample_id = row["sample_id"]

        if pd.isna(sample_id) or str(sample_id).strip() == "":
            raise ValueError("sample_id no puede estar vacío.")

        try:
            request = WineQualityRequest.model_validate(row.drop("sample_id").to_dict())
        except ValueError as error:
            raise ValueError(f"Error en sample_id={sample_id}: {error}") from error

        features = preprocess_wine_request(request)

        quality_band, confidence = infer_wine_quality(
            model["estimator"],
            features,
        )

        prediction = WineQualityPrediction(
            quality_band=quality_band,
            confidence=confidence,
            model_version=model["model_version"],
            preprocessing_version=PREPROCESSING_VERSION,
        )

        predictions.append(
            {
                "sample_id": sample_id,
                **prediction.model_dump(),
            }
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_df = pd.DataFrame(predictions)
    output_df.to_csv(output_path, index=False)

    return len(predictions)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--model", default=DEFAULT_MODEL_PATH, type=Path)
    return parser.parse_args()


def main() -> int:
    arguments = parse_args()

    try:
        prediction_count = predict_file(
            input_path=arguments.input,
            output_path=arguments.output,
            model_path=arguments.model,
        )
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    print(f"Predicciones escritas: {prediction_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
