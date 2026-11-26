from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from starlette.applications import Starlette
from starlette.requests import Request

from api.routes.disease import SymptomRequest, predict_disease
from models.base_model import ModelOutput


class FakeDiseaseModel:
    def __init__(self, ready=True):
        self.is_ready = ready
        self.last_text = None

    def safe_predict(self, model_input):
        self.last_text = model_input.text
        return ModelOutput(
            result={
                "diseases": [
                    {"name": "example condition", "disease_id": 0, "confidence": 0.7}
                ],
                "symptom_count": 2,
            },
            confidence=0.7,
            explanation="Example model ranking; not a diagnosis.",
        )


def make_request(disease_model=None):
    app = Starlette()
    if disease_model is not None:
        app.state.orchestrator = SimpleNamespace(disease_model=disease_model)
    return Request({"type": "http", "app": app})


def test_disease_route_uses_loaded_model_directly():
    model = FakeDiseaseModel()
    request = make_request(model)

    result = predict_disease(
        SymptomRequest(text="  fever, headache  "),
        request,
    )

    assert model.last_text == "fever, headache"
    assert result["result"]["diseases"][0]["name"] == "example condition"
    assert result["confidence"] == 0.7
    assert "not clinical probabilities" in result["disclaimer"]


def test_disease_route_rejects_empty_symptoms():
    model = FakeDiseaseModel()
    request = make_request(model)

    with pytest.raises(HTTPException) as error:
        predict_disease(SymptomRequest(text="   "), request)

    assert error.value.status_code == 400


def test_disease_route_returns_503_when_model_not_ready():
    model = FakeDiseaseModel(ready=False)
    request = make_request(model)

    with pytest.raises(HTTPException) as error:
        predict_disease(SymptomRequest(text="fever"), request)

    assert error.value.status_code == 503


def test_disease_route_returns_503_when_orchestrator_missing():
    request = make_request()

    with pytest.raises(HTTPException) as error:
        predict_disease(SymptomRequest(text="fever"), request)

    assert error.value.status_code == 503
