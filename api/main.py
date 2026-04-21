from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from api.routes import disease, lab, qa, ocr
from core.orchestrator import HealthOrchestrator

app = FastAPI(title="HealthGuard AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(disease.router)
app.include_router(lab.router)
app.include_router(qa.router)
app.include_router(ocr.router)

# ── Initialize orchestrator once ──────────────────
_orchestrator = HealthOrchestrator()

# ── Chat endpoint ─────────────────────────────────
class ChatRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {"status": "running", "message": "HealthGuard AI is live"}

@app.get("/health")
def health():
    return {
        "status": "ok",
        "modules": {
            "disease_predictor": "ready",
            "lab_analyzer":      "ready",
            "medical_qa":        "ready",
            "ocr":               "ready"
        }
    }

@app.post("/reset")
def reset():
    return {"status": "ok"}

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        result = _orchestrator.handle(req.message)
        return {
            "response":    result.get("response", ""),
            "module_used": result.get("module_used", "General Assistant"),
            "confidence":  result.get("confidence", 0.0),
            "raw_result":  result.get("raw_result", {}),
            "disclaimer":  "Not a substitute for professional medical advice."
        }
    except Exception as e:
        return {
            "response":    f"Error processing your request: {str(e)}",
            "module_used": "Error",
            "confidence":  0.0,
            "raw_result":  {},
            "disclaimer":  "Not a substitute for professional medical advice."
        }