from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class QARequest(BaseModel):
    question: str

@router.post("/qa")
def answer_question(request: QARequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    return {
        "result": {"question": request.question},
        "confidence": 0.0,
        "explanation": "QA engine not yet connected",
        "disclaimer": "This is not a substitute for professional medical advice."
    }
