from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from core.orchestrator import HealthOrchestrator

router = APIRouter()
orchestrator = HealthOrchestrator()

class SymptomRequest(BaseModel):
    text: str
    age: Optional[int] = None
    sex: Optional[str] = None

@router.post("/predict/disease")
def predict_disease(request: SymptomRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Symptoms cannot be empty")
    try:
        result = orchestrator.handle(request.text)
        return {
            "result": result.get("raw_result", {}),
            "confidence": result.get("confidence", 0.0),
            "explanation": result.get("response", ""),
            "disclaimer": "This is not a substitute for professional medical advice."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))