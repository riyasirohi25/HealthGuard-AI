"""773-class BioBERT disease classifier with strict checkpoint/mapping validation."""
import json
from pathlib import Path

import torch

from models.base_model import BaseHealthModel, ModelInput, ModelOutput
from config.config import BIOBERT_MODEL, CLEANED_SYMPTOM, SAVED_WEIGHTS_DIR


class DiseasePredictorModel(BaseHealthModel):
    def __init__(self):
        super().__init__()
        self.disease2id = {}
        self.id2disease = {}
        self.num_labels = 0
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    @property
    def artifact_dir(self) -> Path:
        """Preferred self-contained Hugging Face save_pretrained() directory."""
        return SAVED_WEIGHTS_DIR / "disease_predictor"

    @property
    def checkpoint_path(self) -> Path:
        """Recovered Kaggle 773-class state-dict checkpoint."""
        return SAVED_WEIGHTS_DIR / "disease_predictor_773.pt"

    @property
    def mapping_path(self) -> Path:
        """Canonical 773-class mapping belonging to the cleaned Kaggle dataset."""
        return CLEANED_SYMPTOM / "disease2id.json"

    @staticmethod
    def _read_label_mapping(path):
        with Path(path).open(encoding="utf-8") as file:
            raw_mapping = json.load(file)
        if not isinstance(raw_mapping, dict) or not raw_mapping:
            raise ValueError("disease2id.json must be a non-empty JSON object")

        mapping = {str(name): int(label_id) for name, label_id in raw_mapping.items()}
        ids = sorted(mapping.values())
        if len(set(mapping.values())) != len(mapping):
            raise ValueError("Disease label IDs must be unique")
        if ids != list(range(len(mapping))):
            raise ValueError("Disease label IDs must be contiguous from 0")
        return mapping

    def _set_mapping(self, mapping):
        self.disease2id = mapping
        self.num_labels = len(mapping)
        self.id2disease = {
            label_id: name for name, label_id in mapping.items()
        }

    def _load_self_contained_artifacts(self):
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        mapping_path = self.artifact_dir / "disease2id.json"
        if not mapping_path.is_file():
            raise FileNotFoundError(
                f"Model artifact mapping missing: {mapping_path}"
            )
        mapping = self._read_label_mapping(mapping_path)

        tokenizer = AutoTokenizer.from_pretrained(
            str(self.artifact_dir), local_files_only=True
        )
        model = AutoModelForSequenceClassification.from_pretrained(
            str(self.artifact_dir), local_files_only=True
        )
        if model.config.num_labels != len(mapping):
            raise ValueError(
                "Saved model classifier size does not match its disease mapping "
                f"({model.config.num_labels} != {len(mapping)})"
            )

        self._set_mapping(mapping)
        self.tokenizer = tokenizer
        self.model = model.to(self.device)
        self.model.eval()

    @staticmethod
    def _read_state_dict(checkpoint_path):
        try:
            state_dict = torch.load(
                checkpoint_path,
                map_location="cpu",
                weights_only=True,
            )
        except TypeError as exc:
            raise RuntimeError(
                "Safe checkpoint loading requires a PyTorch version supporting "
                "torch.load(weights_only=True). Upgrade PyTorch; do not load this "
                "checkpoint with unrestricted pickle deserialization."
            ) from exc

        if isinstance(state_dict, dict):
            for key in ("state_dict", "model_state_dict", "model"):
                if isinstance(state_dict.get(key), dict):
                    state_dict = state_dict[key]
                    break
        if not isinstance(state_dict, dict) or not state_dict:
            raise ValueError("BioBERT checkpoint is not a non-empty state dictionary")
        return state_dict

    def _load_kaggle_checkpoint(self):
        from transformers import (
            AutoConfig,
            AutoModelForSequenceClassification,
            AutoTokenizer,
        )

        mapping = self._read_label_mapping(self.mapping_path)
        if len(mapping) != 773:
            raise ValueError(
                "The recovered Kaggle checkpoint is a 773-class model, but "
                f"the canonical mapping contains {len(mapping)} labels. "
                "Check data/cleaned/symptom_disease/disease2id.json."
            )

        # Build the exact architecture from the configured local BioBERT base.
        # HEALTHGUARD_BIOBERT_BASE may point at a local Hugging Face snapshot
        # when this machine cannot reach the Hugging Face Hub.
        config = AutoConfig.from_pretrained(
            BIOBERT_MODEL,
            local_files_only=True,
        )
        if getattr(config, "model_type", None) != "bert":
            raise ValueError(
                f"Expected a BERT checkpoint base, got {config.model_type!r}"
            )
        if getattr(config, "hidden_size", None) != 768:
            raise ValueError(
                f"Expected BioBERT hidden size 768, got {config.hidden_size}"
            )

        config.num_labels = len(mapping)
        config.label2id = dict(mapping)
        config.id2label = {
            int(label_id): disease for disease, label_id in mapping.items()
        }

        model = AutoModelForSequenceClassification.from_config(config)
        state_dict = self._read_state_dict(self.checkpoint_path)

        # Strict loading verifies every expected tensor name and shape, including
        # the 773 x 768 classifier matrix. No classifier weights are reinitialized.
        incompatible = model.load_state_dict(state_dict, strict=True)
        if incompatible.missing_keys or incompatible.unexpected_keys:
            raise ValueError(
                "Checkpoint tensors do not exactly match BioBERT architecture: "
                f"missing={incompatible.missing_keys}, "
                f"unexpected={incompatible.unexpected_keys}"
            )
        if model.classifier.out_features != len(mapping):
            raise ValueError(
                "Loaded classifier output size does not match the disease mapping"
            )

        tokenizer = AutoTokenizer.from_pretrained(
            BIOBERT_MODEL,
            local_files_only=True,
        )
        if len(tokenizer) > config.vocab_size:
            raise ValueError(
                "BioBERT tokenizer vocabulary is larger than the model vocabulary"
            )

        self._set_mapping(mapping)
        self.tokenizer = tokenizer
        self.model = model.to(self.device)
        self.model.eval()
        print(
            "Loaded recovered Kaggle BioBERT checkpoint — "
            f"{self.num_labels} disease classes"
        )

    def load(self):
        """Load self-contained artifacts first, otherwise the recovered 773-class file."""
        self.is_ready = False
        self.model = None
        self.tokenizer = None
        self.disease2id = {}
        self.id2disease = {}
        self.num_labels = 0

        try:
            if (
                (self.artifact_dir / "config.json").is_file()
                and (self.artifact_dir / "disease2id.json").is_file()
            ):
                self._load_self_contained_artifacts()
            elif self.checkpoint_path.is_file() and self.mapping_path.is_file():
                self._load_kaggle_checkpoint()
            else:
                print(
                    "BioBERT artifacts not found. Expected either a complete "
                    f"model directory at {self.artifact_dir} or checkpoint "
                    f"{self.checkpoint_path} plus mapping {self.mapping_path}."
                )
                return

            self.is_ready = True
            print(f"Disease predictor ready — {self.num_labels} classes")
        except Exception as exc:
            self.model = None
            self.tokenizer = None
            self.is_ready = False
            print(f"Could not load BioBERT disease predictor: {exc}")

    def predict(self, input: ModelInput) -> ModelOutput:
        if not self.is_ready or self.model is None or self.tokenizer is None:
            raise RuntimeError("BioBERT disease predictor is not loaded")
        if not isinstance(input.text, str) or not input.text.strip():
            raise ValueError("Symptoms text must be a non-empty string")

        encoded = self.tokenizer(
            input.text.strip(),
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding=True,
        )
        encoded = {key: value.to(self.device) for key, value in encoded.items()}

        with torch.inference_mode():
            outputs = self.model(**encoded)
            scores = torch.softmax(outputs.logits, dim=1)[0]

        top = torch.topk(scores, k=min(3, self.num_labels))
        diseases = [
            {
                "name": self.id2disease[int(index.item())],
                "confidence": round(float(score.item()), 4),
                "disease_id": int(index.item()),
            }
            for score, index in zip(top.values, top.indices)
        ]

        top_name = diseases[0]["name"] if diseases else "unknown"
        symptom_count = len(
            [part for part in input.text.split(",") if part.strip()]
        )
        return ModelOutput(
            result={
                "diseases": diseases,
                "symptom_count": symptom_count,
            },
            confidence=diseases[0]["confidence"] if diseases else 0.0,
            explanation=(
                f"BioBERT ranked {top_name} highest among its 773 trained classes. "
                "The model score is not a clinical probability or diagnosis; "
                "consult a qualified clinician."
            ),
            sources=["biobert_classifier", "kaggle_773_disease_dataset"],
        )
