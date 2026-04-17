import json
from config.config import CLEANED_LAB

lab_reference = {
    "hemoglobin": {"min": 12.0, "max": 17.5, "unit": "g/dL",
        "low": "Anemia possible", "high": "Polycythemia possible"},
    "hematocrit": {"min": 36.0, "max": 52.0, "unit": "%",
        "low": "Anemia possible", "high": "Dehydration or polycythemia"},
    "wbc": {"min": 4.5, "max": 11.0, "unit": "10^3/uL",
        "low": "Leukopenia - infection risk", "high": "Leukocytosis - infection or inflammation"},
    "platelets": {"min": 150.0, "max": 400.0, "unit": "10^3/uL",
        "low": "Thrombocytopenia - bleeding risk", "high": "Thrombocytosis"},
    "glucose": {"min": 70.0, "max": 100.0, "unit": "mg/dL",
        "low": "Hypoglycemia", "high": "Hyperglycemia or diabetes"},
    "sodium": {"min": 136.0, "max": 145.0, "unit": "mEq/L",
        "low": "Hyponatremia", "high": "Hypernatremia"},
    "potassium": {"min": 3.5, "max": 5.0, "unit": "mEq/L",
        "low": "Hypokalemia - muscle weakness", "high": "Hyperkalemia - cardiac risk"},
    "creatinine": {"min": 0.6, "max": 1.2, "unit": "mg/dL",
        "low": "Low muscle mass", "high": "Kidney dysfunction"},
    "bun": {"min": 7.0, "max": 20.0, "unit": "mg/dL",
        "low": "Malnutrition or liver disease", "high": "Kidney disease or dehydration"},
    "alt": {"min": 7.0, "max": 56.0, "unit": "U/L",
        "low": "Normal", "high": "Liver damage or disease"},
    "ast": {"min": 10.0, "max": 40.0, "unit": "U/L",
        "low": "Normal", "high": "Liver or heart damage"},
    "total_cholesterol": {"min": 0.0, "max": 200.0, "unit": "mg/dL",
        "low": "Normal", "high": "High cardiovascular risk"},
    "hdl": {"min": 40.0, "max": 999.0, "unit": "mg/dL",
        "low": "Low HDL - cardiovascular risk", "high": "Normal"},
    "ldl": {"min": 0.0, "max": 100.0, "unit": "mg/dL",
        "low": "Normal", "high": "High cardiovascular risk"},
    "tsh": {"min": 0.4, "max": 4.0, "unit": "mIU/L",
        "low": "Hyperthyroidism possible", "high": "Hypothyroidism possible"},
    "calcium": {"min": 8.5, "max": 10.5, "unit": "mg/dL",
        "low": "Hypocalcemia", "high": "Hypercalcemia"},
    "hba1c": {"min": 0.0, "max": 5.7, "unit": "%",
        "low": "Normal", "high": "Diabetes or prediabetes"},
}

CLEANED_LAB.mkdir(parents=True, exist_ok=True)
with open(CLEANED_LAB / 'lab_reference.json', 'w') as f:
    json.dump(lab_reference, f, indent=2)

print(f"✅ Done! {len(lab_reference)} lab tests saved.")