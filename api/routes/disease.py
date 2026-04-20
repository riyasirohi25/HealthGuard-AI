from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class SymptomRequest(BaseModel):
    text: str

@router.post("/predict/disease")
def predict_disease(request: SymptomRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Empty input")
    return {"result": "dummy disease"}