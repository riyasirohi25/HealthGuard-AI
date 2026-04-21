from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.orchestrator import HealthOrchestrator

router = APIRouter()
orchestrator = HealthOrchestrator()

class QARequest(BaseModel):
    question: str

@router.post("/qa")
def answer_question(request: QARequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    try:
        result = orchestrator.handle(request.question)
        return {
            "result": result.get("raw_result", {}),
            "confidence": result.get("confidence", 0.0),
            "explanation": result.get("response", ""),
            "disclaimer": "This is not a substitute for professional medical advice."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))