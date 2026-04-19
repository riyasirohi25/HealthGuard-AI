# api/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from config.config import APP_NAME, API_VERSION, API_HOST, API_PORT
from core.orchestrator import HealthOrchestrator

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

# Load orchestrator once at startup
orchestrator = None

@app.on_event("startup")
def startup_event():
    global orchestrator
    orchestrator = HealthOrchestrator()

# ── Request Schemas ───────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class SymptomRequest(BaseModel):
    text: str
    age: Optional[int] = None
    sex: Optional[str] = None

class LabRequest(BaseModel):
    test_name: str
    value: float
    sex: Optional[str] = None

class QARequest(BaseModel):
    question: str

# ── Routes ───────────────────────────────────────
@app.get("/")
def root():
    return {
        "app": APP_NAME,
        "version": API_VERSION,
        "status": "running"
    }

@app.get("/health")
def health():
    status = orchestrator.get_module_status() if orchestrator else {}
    return {"status": "ok", "version": API_VERSION, "modules": status}

@app.post("/chat")
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    result = orchestrator.handle(request.message)
    result["disclaimer"] = "This is not a substitute for professional medical advice."
    return result

@app.post("/predict/disease")
def predict_disease(request: SymptomRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Symptoms cannot be empty")
    result = orchestrator.handle(request.text)
    result["disclaimer"] = "This is not a substitute for professional medical advice."
    return result

@app.post("/analyze/lab")
def analyze_lab(request: LabRequest):
    message = f"My {request.test_name} is {request.value}"
    if request.sex:
        message += f" and I am {request.sex}"
    result = orchestrator.handle(message)
    result["disclaimer"] = "This is not a substitute for professional medical advice."
    return result

@app.post("/qa")
def answer_question(request: QARequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    result = orchestrator.handle(request.question)
    result["disclaimer"] = "This is not a substitute for professional medical advice."
    return result

@app.post("/reset")
def reset_conversation():
    orchestrator.reset_conversation()
    return {"status": "conversation reset"}

if __name__ == "__main__":
    uvicorn.run("api.main:app", host=API_HOST, port=API_PORT, reload=True)