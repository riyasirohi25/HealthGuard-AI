from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from config.config import APP_NAME, API_VERSION, API_HOST, API_PORT

app = FastAPI(
    title=APP_NAME,
    description="AI-powered medical assistant — self hosted, no external APIs",
    version=API_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SymptomRequest(BaseModel):
    text: str
    age: Optional[int] = None
    sex: Optional[str] = None

class LabRequest(BaseModel):
    test_name: str
    value: float
    sex: Optional[str] = None
    age: Optional[int] = None

class QARequest(BaseModel):
    question: str

class PredictionResponse(BaseModel):
    result: dict
    confidence: float
    explanation: str
    sources: list = []
    error: Optional[str] = None
    disclaimer: str = "This is not a substitute for professional medical advice."

@app.get("/")
def root():
    return {
        "app": APP_NAME,
        "version": API_VERSION,
        "status": "running",
        "endpoints": [
            "/predict/disease",
            "/analyze/lab",
            "/qa",
            "/health"
        ]
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": API_VERSION,
        "modules": {
            "disease_predictor": "not loaded",
            "lab_analyzer":      "not loaded",
            "qa_engine":         "not loaded",
            "summarizer":        "not loaded"
        }
    }

@app.post("/predict/disease", response_model=PredictionResponse)
def predict_disease(request: SymptomRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Symptoms text cannot be empty")
    return PredictionResponse(
        result={"diseases": [], "symptoms_received": request.text},
        confidence=0.0,
        explanation="Disease predictor model not yet connected",
    )

@app.post("/analyze/lab", response_model=PredictionResponse)
def analyze_lab(request: LabRequest):
    if request.value < 0:
        raise HTTPException(status_code=400, detail="Lab value cannot be negative")
    return PredictionResponse(
        result={"test": request.test_name, "value": request.value, "status": "pending"},
        confidence=0.0,
        explanation="Lab analyzer not yet connected",
    )

@app.post("/qa", response_model=PredictionResponse)
def answer_question(request: QARequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    return PredictionResponse(
        result={"question": request.question},
        confidence=0.0,
        explanation="QA engine not yet connected",
    )

if __name__ == "__main__":
    uvicorn.run("api.main:app", host=API_HOST, port=API_PORT, reload=True)