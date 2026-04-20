from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
from config.config import CLEANED_LAB

router = APIRouter()

ref_path = CLEANED_LAB / "lab_reference_ranges.json"
with open(ref_path) as f:
    LAB_REFERENCE = json.load(f)

class LabRequest(BaseModel):
    test_name: str
    value: float
    sex: Optional[str] = None

@router.post("/analyze/lab")
def analyze_lab(request: LabRequest):
    if request.value < 0:
        raise HTTPException(status_code=400, detail="Value cannot be negative")

    test = request.test_name.lower().replace(" ", "_")

    if test not in LAB_REFERENCE:
        return {
            "result": {"status": "unknown_test", "test": test},
            "confidence": 0.0,
            "explanation": f"No reference range found for '{test}'",
            "disclaimer": "This is not a substitute for professional medical advice."
        }

    ref = LAB_REFERENCE[test]

    if request.sex and request.sex.lower() in ref:
        range_ = ref[request.sex.lower()]
    else:
        range_ = ref.get("general", {})

    low = range_.get("low", float("-inf"))
    high = range_.get("high", float("inf"))
    crit_low = ref.get("critical_low", float("-inf"))
    crit_high = ref.get("critical_high", float("inf"))
    unit = ref.get("unit", "")
    desc = ref.get("description", "")

    val = float(request.value)

    if val <= crit_low:
        status = "CRITICALLY LOW"
        explanation = f"{test} is critically low ({val} {unit}). Seek immediate medical attention. {desc}"
        confidence = 0.99
    elif val >= crit_high:
        status = "CRITICALLY HIGH"
        explanation = f"{test} is critically high ({val} {unit}). Seek immediate medical attention. {desc}"
        confidence = 0.99
    elif val < low:
        status = "LOW"
        explanation = f"{test} is below normal range ({low}–{high} {unit}). {desc}"
        confidence = 0.95
    elif val > high:
        status = "HIGH"
        explanation = f"{test} is above normal range ({low}–{high} {unit}). {desc}"
        confidence = 0.95
    else:
        status = "NORMAL"
        explanation = f"{test} is within normal range ({low}–{high} {unit}). {desc}"
        confidence = 0.99

    return {
        "result": {
            "test": test,
            "value": val,
            "status": status,
            "normal_range": f"{low}–{high}",
            "unit": unit
        },
        "confidence": confidence,
        "explanation": explanation,
        "sources": ["lab_reference_ranges_v1"],
        "disclaimer": "This is not a substitute for professional medical advice."
    }
