from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from config.config import (
    APP_NAME, API_VERSION,
    DISEASE_MODEL_DIR, LAB_MODEL_DIR, QA_MODEL_DIR,
    CLEANED_SYMPTOM
)

app = FastAPI(title=APP_NAME, version=API_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load models ──────────────────────────────────────────
print("Loading models...")

with open(DISEASE_MODEL_DIR / 'model.pkl', 'rb') as f:
    disease_model = pickle.load(f)
with open(DISEASE_MODEL_DIR / 'all_symptoms.json') as f:
    all_symptoms = json.load(f)
with open(DISEASE_MODEL_DIR / 'id2disease.json') as f:
    id2disease = json.load(f)

with open(LAB_MODEL_DIR / 'lab_reference.json') as f:
    lab_reference = json.load(f)

with open(QA_MODEL_DIR / 'vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)
with open(QA_MODEL_DIR / 'tfidf_matrix.pkl', 'rb') as f:
    tfidf_matrix = pickle.load(f)
qa_df = pd.read_csv(QA_MODEL_DIR / 'qa_database.csv')

print("✅ All models loaded!")

# ── Request models ────────────────────────────────────────
class SymptomRequest(BaseModel):
    symptoms: List[str]
    top_k: Optional[int] = 3

class LabRequest(BaseModel):
    test_name: str
    value: float

class QARequest(BaseModel):
    question: str
    top_k: Optional[int] = 3

# ── Routes ────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": f"Welcome to {APP_NAME}", "version": API_VERSION}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/symptoms")
def get_symptoms():
    return {"symptoms": all_symptoms, "count": len(all_symptoms)}

@app.post("/predict/disease")
def predict_disease(req: SymptomRequest):
    vec = np.zeros(len(all_symptoms))
    matched = []
    for sym in req.symptoms:
        sym = sym.lower().strip().replace('_', ' ')
        if sym in all_symptoms:
            vec[all_symptoms.index(sym)] = 1
            matched.append(sym)
    if not matched:
        raise HTTPException(status_code=400, detail="No recognized symptoms found")
    proba = disease_model.predict_proba([vec])[0]
    top_indices = np.argsort(proba)[::-1][:req.top_k]
    results = []
    for idx in top_indices:
        if proba[idx] > 0.01:
            results.append({
                "disease": id2disease[str(idx)],
                "confidence": round(float(proba[idx]), 4)
            })
    return {"matched_symptoms": matched, "predictions": results}

@app.post("/analyze/lab")
def analyze_lab(req: LabRequest):
    name = req.test_name.lower().strip()
    if name not in lab_reference:
        raise HTTPException(status_code=404, detail=f"Test '{name}' not found")
    ref = lab_reference[name]
    if req.value < ref["min"]:
        status = "low"
        interpretation = ref["low"]
    elif req.value > ref["max"]:
        status = "high"
        interpretation = ref["high"]
    else:
        status = "normal"
        interpretation = "Within normal range"
    return {
        "test": name,
        "value": req.value,
        "unit": ref["unit"],
        "normal_range": f"{ref['min']} - {ref['max']}",
        "status": status,
        "interpretation": interpretation
    }

@app.post("/qa")
def answer_question(req: QARequest):
    from sklearn.metrics.pairwise import cosine_similarity
    query_vec = vectorizer.transform([req.question])
    scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = np.argsort(scores)[::-1][:req.top_k]
    results = []
    for idx in top_indices:
        if scores[idx] > 0.01:
            results.append({
                "question": qa_df.iloc[idx]["question"],
                "answer": qa_df.iloc[idx]["answer"],
                "score": round(float(scores[idx]), 4)
            })
    if not results:
        raise HTTPException(status_code=404, detail="No relevant answer found")
    return {"query": req.question, "results": results}

@app.get("/lab/tests")
def get_lab_tests():
    return {"tests": list(lab_reference.keys()), "count": len(lab_reference)}