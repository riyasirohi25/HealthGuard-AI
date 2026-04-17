import json
import numpy as np
import pickle
from config.config import CLEANED_LAB, LAB_MODEL_DIR

with open(CLEANED_LAB / 'lab_reference.json') as f:
    lab_reference = json.load(f)

def analyze_lab(test_name, value):
    test_name = test_name.lower().strip()
    if test_name not in lab_reference:
        return {"status": "unknown", "message": "Test not in reference range database"}
    ref = lab_reference[test_name]
    result = {
        "test": test_name,
        "value": value,
        "unit": ref["unit"],
        "normal_min": ref["min"],
        "normal_max": ref["max"],
    }
    if value < ref["min"]:
        result["status"] = "low"
        result["interpretation"] = ref["low"]
    elif value > ref["max"]:
        result["status"] = "high"
        result["interpretation"] = ref["high"]
    else:
        result["status"] = "normal"
        result["interpretation"] = "Within normal range"
    return result

# Save analyzer
LAB_MODEL_DIR.mkdir(parents=True, exist_ok=True)

with open(LAB_MODEL_DIR / 'lab_reference.json', 'w') as f:
    json.dump(lab_reference, f, indent=2)

with open(LAB_MODEL_DIR / 'analyzer.pkl', 'wb') as f:
    pickle.dump(analyze_lab, f)

# Quick test
print("Testing lab analyzer...")
tests = [
    ("hemoglobin", 10.5),
    ("glucose", 95.0),
    ("potassium", 6.2),
    ("tsh", 2.1),
]
for name, val in tests:
    result = analyze_lab(name, val)
    print(f"  {name}: {val} → {result['status']} ({result['interpretation']})")

print(f"\n✅ Done! Lab analyzer saved to models/lab_analyzer/")