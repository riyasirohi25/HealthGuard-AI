from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from starlette.applications import Starlette
from starlette.requests import Request

from api.routes.qa import QARequest, answer_question


class FakeOrchestrator:
    def __init__(self):
        self.last_message = None

    def handle(self, message):
        self.last_message = message
        return {
            "raw_result": {"retrieved_chunks": 2},
            "confidence": 0.8,
            "response": "Example answer",
        }


def make_request(orchestrator=None):
    app = Starlette()
    if orchestrator is not None:
        app.state.orchestrator = orchestrator
    return Request({"type": "http", "app": app})


def test_qa_route_uses_shared_orchestrator():
    orchestrator = FakeOrchestrator()
    result = answer_question(
        QARequest(question="  What causes a cough?  "),
        make_request(orchestrator),
    )

    assert orchestrator.last_message == "What causes a cough?"
    assert result["result"] == {"retrieved_chunks": 2}
    assert result["explanation"] == "Example answer"


def test_qa_route_rejects_empty_question():
    with pytest.raises(HTTPException) as error:
        answer_question(QARequest(question="  "), make_request(FakeOrchestrator()))
    assert error.value.status_code == 400


def test_qa_route_returns_503_without_shared_orchestrator():
    with pytest.raises(HTTPException) as error:
        answer_question(QARequest(question="What causes a cough?"), make_request())
    assert error.value.status_code == 503
