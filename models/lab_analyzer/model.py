# models/lab_analyzer/model.py

import json
from models.base_model import BaseHealthModel, ModelInput, ModelOutput
from config.config import CLEANED_LAB


class LabAnalyzerModel(BaseHealthModel):

    def __init__(self):
        super().__init__()
        self.reference_ranges = {}

    def load(self):
        ref_path = CLEANED_LAB / "lab_reference_ranges.json"
        if ref_path.exists():
            with open(ref_path) as f:
                self.reference_ranges = json.load(f)
            self.is_ready = True
            print(f"Lab analyzer loaded — {len(self.reference_ranges)} tests")
        else:
            print("lab_reference_ranges.json not found — run data cleaning first")

    def predict(self, input: ModelInput) -> ModelOutput:
        test  = input.metadata.get("test_name", "").lower().replace(" ", "_")
        value = input.metadata.get("value", 0)
        sex   = input.metadata.get("sex", None)

        if test not in self.reference_ranges:
            return ModelOutput(
                result={"status": "unknown_test", "test": test},
                confidence=0.0,
                explanation=f"No reference range found for '{test}'"
            )

        ref = self.reference_ranges[test]

        if sex and sex.lower() in ref:
            range_ = ref[sex.lower()]
        else:
            range_ = ref.get("general", {})

        low       = range_.get("low",  float("-inf"))
        high      = range_.get("high", float("inf"))
        crit_low  = ref.get("critical_low",  float("-inf"))
        crit_high = ref.get("critical_high", float("inf"))
        unit      = ref.get("unit", "")
        desc      = ref.get("description", "")

        try:
            val = float(value)
        except:
            return ModelOutput(
                result={"status": "invalid_value"},
                confidence=0.0,
                explanation="Invalid value provided"
            )

        if val <= crit_low:
            status      = "CRITICALLY LOW"
            explanation = f"{test} is critically low ({val} {unit}). Seek immediate medical attention."
            confidence  = 0.99
        elif val >= crit_high:
            status      = "CRITICALLY HIGH"
            explanation = f"{test} is critically high ({val} {unit}). Seek immediate medical attention."
            confidence  = 0.99
        elif val < low:
            status      = "LOW"
            explanation = f"{test} is below normal range ({low}–{high} {unit}). {desc}"
            confidence  = 0.95
        elif val > high:
            status      = "HIGH"
            explanation = f"{test} is above normal range ({low}–{high} {unit}). {desc}"
            confidence  = 0.95
        else:
            status      = "NORMAL"
            explanation = f"{test} is within normal range ({low}–{high} {unit}). {desc}"
            confidence  = 0.99

        return ModelOutput(
            result={
                "test":         test,
                "value":        val,
                "status":       status,
                "normal_range": f"{low}–{high}",
                "unit":         unit
            },
            confidence=confidence,
            explanation=explanation,
            sources=["lab_reference_ranges_v1"]
        )