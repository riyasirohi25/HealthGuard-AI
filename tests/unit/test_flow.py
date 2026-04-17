import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_full_symptom_flow():
    res = client.post("/predict/disease", json={
        "text": "fever, headache, joint pain",
        "age": 25,
        "sex": "female"
    })
    assert res.status_code == 200
    data = res.json()
    assert "result" in data
    assert "confidence" in data
    assert "explanation" in data
    assert "disclaimer" in data

def test_full_lab_flow():
    res = client.post("/analyze/lab", json={
        "test_name": "glucose_fasting",
        "value": 145.0,
        "sex": "male"
    })
    assert res.status_code == 200
    data = res.json()
    assert "result" in data
    assert data["result"]["test"] == "glucose_fasting"

def test_full_qa_flow():
    res = client.post("/qa", json={
        "question": "What causes high blood pressure?"
    })
    assert res.status_code == 200
    assert "explanation" in res.json()