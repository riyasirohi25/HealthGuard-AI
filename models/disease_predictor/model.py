import json
import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from models.base_model import BaseHealthModel, ModelInput, ModelOutput
from config.config import BIOBERT_MODEL, SAVED_WEIGHTS_DIR, CLEANED_SYMPTOM


class DiseasePredictorModel(BaseHealthModel):

    def __init__(self):
        super().__init__()
        self.disease2id = {}
        self.id2disease = {}
        self.num_labels = 0

    def load(self):
        # Load disease mapping
        mapping_path = CLEANED_SYMPTOM / "disease2id.json"
        if not mapping_path.exists():
            print("disease2id.json not found — run data cleaning first")
            return

        with open(mapping_path) as f:
            self.disease2id = json.load(f)
        self.id2disease = {v: k for k, v in self.disease2id.items()}
        self.num_labels = len(self.disease2id)

        # Load fine-tuned weights if they exist
        weights_path = SAVED_WEIGHTS_DIR / "disease_predictor.pt"
        if weights_path.exists():
            self.tokenizer = AutoTokenizer.from_pretrained(BIOBERT_MODEL)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                BIOBERT_MODEL, num_labels=self.num_labels
            )
            self.model.load_state_dict(torch.load(weights_path, map_location="cpu"))
            self.model.eval()
            self.is_ready = True
            print(f"Disease predictor loaded — {self.num_labels} diseases")
        else:
            print("No trained weights found — model needs training first")

    def predict(self, input: ModelInput) -> ModelOutput:
        inputs = self.tokenizer(
            input.text,
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding=True
        )
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1)[0]

        top3 = torch.topk(probs, k=min(3, self.num_labels))
        diseases = []
        for score, idx in zip(top3.values, top3.indices):
            diseases.append({
                "name": self.id2disease[idx.item()],
                "confidence": round(score.item(), 3),
                "disease_id": idx.item()
            })

        top_confidence = diseases[0]["confidence"] if diseases else 0.0
        top_name = diseases[0]["name"] if diseases else "unknown"

        return ModelOutput(
            result={"diseases": diseases, "symptom_count": len(input.text.split(","))},
            confidence=top_confidence,
            explanation=f"Based on your symptoms, the most likely condition is {top_name}. Please consult a doctor for confirmation.",
            sources=["biobert_classifier", "symptom_disease_dataset_v1"]
        )