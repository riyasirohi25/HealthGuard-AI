from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

from models.base_model import ModelInput

router = APIRouter()


class SymptomRequest(BaseModel):
    text: str
    age: Optional[int] = None
    sex: Optional[str] = None


@router.post("/predict/disease")
def predict_disease(request: SymptomRequest, http_request: Request):
    """Run BioBERT directly; disease prediction must not depend on LLM intent parsing."""
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Symptoms cannot be empty")

    orchestrator = getattr(http_request.app.state, "orchestrator", None)
    if orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="HealthGuard AI services are not initialized",
        )

    disease_model = getattr(orchestrator, "disease_model", None)
    if disease_model is None or not disease_model.is_ready:
        raise HTTPException(
            status_code=503,
            detail="BioBERT disease predictor is not available",
        )

    model_output = disease_model.safe_predict(
        ModelInput(text=request.text.strip())
    )
    if model_output.error:
        raise HTTPException(
            status_code=500,
            detail="Disease prediction failed; check the backend logs.",
        )

    return {
        "result": model_output.result,
        "confidence": model_output.confidence,
        "explanation": model_output.explanation,
        "disclaimer": (
            "Model scores are informational rankings, not clinical probabilities "
            "or a diagnosis. Consult a qualified healthcare professional."
        ),
    }
