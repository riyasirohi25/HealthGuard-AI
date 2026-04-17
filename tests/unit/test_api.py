import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_root():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "running"

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_disease_predict_empty():
    res = client.post("/predict/disease", json={"text": ""})
    assert res.status_code == 400

def test_disease_predict_valid():
    res = client.post("/predict/disease", json={"text": "fever and headache"})
    assert res.status_code == 200
    assert "result" in res.json()
    assert "disclaimer" in res.json()

def test_lab_analyze_valid():
    res = client.post("/analyze/lab", json={"test_name": "hemoglobin", "value": 12.0})
    assert res.status_code == 200
    assert "result" in res.json()

def test_lab_analyze_negative():
    res = client.post("/analyze/lab", json={"test_name": "hemoglobin", "value": -1.0})
    assert res.status_code == 400

def test_qa_valid():
    res = client.post("/qa", json={"question": "What is normal blood pressure?"})
    assert res.status_code == 200
    assert "explanation" in res.json()

def test_qa_empty():
    res = client.post("/qa", json={"question": ""})
    assert res.status_code == 400