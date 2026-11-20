"""S9.4 — Tests que escribe el alumnado.

Cada test empieza en rojo con `pytest.fail`. Sustituye esa línea por el test
real; la entrega se considera completa cuando toda la suite está en verde.
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from wine_api.dependencies import get_predictor  # noqa: F401 - pista S9.4a
from wine_api.export_openapi import render_openapi
from wine_api.predictor import UnavailablePredictor  # noqa: F401 - pista S9.4a


def test_prediction_returns_503_when_model_is_unavailable(
    client: TestClient, valid_payload: dict
) -> None:
    client.app.dependency_overrides[get_predictor] = lambda: UnavailablePredictor()
    try:
        response = client.post("/v1/predictions", json=valid_payload)

        assert response.status_code == 503
        assert response.json()["error"]["code"] == "model_unavailable"
    finally:
        client.app.dependency_overrides.pop(get_predictor, None)


@pytest.mark.parametrize("alcohol", [4.9, 20.1, None, "mucho", True])
def test_out_of_contract_values_are_rejected(
    client: TestClient, valid_payload: dict, alcohol: object
) -> None:
    valid_payload["features"]["alcohol"] = alcohol

    response = client.post("/v1/predictions", json=valid_payload)

    assert response.status_code == 422
    fields = response.json()["error"]["fields"]
    assert [field["field"] for field in fields] == ["features.alcohol"]


def test_range_limits_are_inclusive(client: TestClient, valid_payload: dict) -> None:
    for alcohol in (5, 20):
        valid_payload["features"]["alcohol"] = alcohol
        response = client.post("/v1/predictions", json=valid_payload)

        assert response.status_code == 200


def test_openapi_matches_versioned_contract() -> None:
    contract_path = Path(__file__).resolve().parents[1] / "contracts" / "openapi.json"

    assert render_openapi() == contract_path.read_text(encoding="utf-8")
