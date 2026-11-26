from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()


class QARequest(BaseModel):
    question: str


@router.post("/qa")
def answer_question(request: QARequest, http_request: Request):
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    orchestrator = getattr(http_request.app.state, "orchestrator", None)
    if orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="HealthGuard AI services are not initialized",
        )

    try:
        result = orchestrator.handle(request.question.strip())
        return {
            "result": result.get("raw_result", {}),
            "confidence": result.get("confidence", 0.0),
            "explanation": result.get("response", ""),
            "disclaimer": "This is not a substitute for professional medical advice.",
        }
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Medical Q&A request failed; check the backend logs.",
        )
