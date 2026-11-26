"""Fine-tune BioBERT on the 773-class cleaned symptom/disease dataset.

Expected input: data/cleaned/symptom_disease/symptoms_diseases_clean.csv
Required columns: disease, symptoms_text
Optional source column: disease_id (validated against the canonical alphabetical map).
Singleton diseases remain in training; they are excluded from validation because a
single example cannot appear in both partitions without leakage.
"""
import json
import random
import shutil

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader

from config.config import BIOBERT_MODEL, CLEANED_SYMPTOM, SAVED_WEIGHTS_DIR


SEED = 42
EPOCHS = 10
BATCH_SIZE = 16
LEARNING_RATE = 3e-5
MAX_LENGTH = 128
VALIDATION_SIZE = 0.2


def set_seed(seed=SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class SymptomDataset(Dataset):
    def __init__(self, frame, tokenizer, disease2id):
        self.texts = frame["symptoms_text"].astype(str).tolist()
        self.labels = [disease2id[name] for name in frame["disease"]]
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, index):
        encoded = self.tokenizer(
            self.texts[index],
            max_length=MAX_LENGTH,
            truncation=True,
            padding="max_length",
            return_tensors="pt",
        )
        return {
            "input_ids": encoded["input_ids"].squeeze(0),
            "attention_mask": encoded["attention_mask"].squeeze(0),
            "labels": torch.tensor(self.labels[index], dtype=torch.long),
        }


def load_training_data():
    csv_path = CLEANED_SYMPTOM / "symptoms_diseases_clean.csv"
    if not csv_path.is_file():
        raise FileNotFoundError(
            f"Training data not found: {csv_path}. "
            "Place the 773-class Kaggle CSV there; do not run the separate "
            "41-class legacy source cleaner over this directory."
        )

    frame = pd.read_csv(csv_path)
    required = {"disease", "symptoms_text"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Training CSV is missing required columns: {sorted(missing)}")

    frame = frame.dropna(subset=["disease", "symptoms_text"]).copy()
    frame["disease"] = frame["disease"].astype(str).str.strip().str.lower()
    frame["symptoms_text"] = frame["symptoms_text"].astype(str).str.strip()
    frame = frame[
        (frame["disease"] != "") & (frame["symptoms_text"] != "")
    ].reset_index(drop=True)
    if frame.empty:
        raise ValueError("Training CSV contains no usable disease/symptom rows")

    labels = sorted(frame["disease"].unique())
    disease2id = {name: index for index, name in enumerate(labels)}

    # When the prepared CSV has disease_id, validate the original data mapping
    # rather than silently replacing potentially different label IDs.
    if "disease_id" in frame.columns:
        numeric_ids = pd.to_numeric(frame["disease_id"], errors="coerce")
        if numeric_ids.isna().any():
            raise ValueError("disease_id contains missing or non-numeric values")
        frame["disease_id"] = numeric_ids.astype(int)
        observed = frame[["disease", "disease_id"]].drop_duplicates()
        disease_to_ids = observed.groupby("disease")["disease_id"].nunique()
        id_to_diseases = observed.groupby("disease_id")["disease"].nunique()
        if (disease_to_ids > 1).any() or (id_to_diseases > 1).any():
            raise ValueError("CSV disease_id values do not define a one-to-one label map")
        csv_mapping = {
            str(name): int(label_id)
            for name, label_id in observed[["disease", "disease_id"]].itertuples(
                index=False, name=None
            )
        }
        if csv_mapping != disease2id:
            raise ValueError(
                "CSV disease_id values do not match the alphabetical mapping. "
                "Do not train until the exact Kaggle mapping is restored."
            )

    frame["label"] = frame["disease"].map(disease2id)
    return frame, disease2id


def build_train_validation_split(
    frame, validation_fraction=VALIDATION_SIZE, seed=SEED
):
    """Split each class independently; singleton samples remain in training only."""
    if not 0.0 < validation_fraction < 1.0:
        raise ValueError("validation_fraction must be between 0 and 1")

    rng = np.random.default_rng(seed)
    train_indices = []
    validation_indices = []
    singleton_labels = []

    for label, group in frame.groupby("label", sort=True):
        indices = group.index.to_numpy().copy()
        rng.shuffle(indices)
        if len(indices) == 1:
            train_indices.extend(indices.tolist())
            singleton_labels.append(int(label))
            continue

        validation_count = max(1, int(round(len(indices) * validation_fraction)))
        validation_count = min(validation_count, len(indices) - 1)
        validation_indices.extend(indices[:validation_count].tolist())
        train_indices.extend(indices[validation_count:].tolist())

    if not train_indices or not validation_indices:
        raise ValueError(
            "Not enough data to form non-empty train and validation partitions"
        )

    train_frame = frame.loc[train_indices].sample(
        frac=1, random_state=seed
    ).reset_index(drop=True)
    validation_frame = frame.loc[validation_indices].sample(
        frac=1, random_state=seed
    ).reset_index(drop=True)
    return train_frame, validation_frame, singleton_labels


def evaluate(model, loader, device):
    model.eval()
    correct = 0
    total = 0
    with torch.inference_mode():
        for batch in loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            logits = model(
                input_ids=input_ids, attention_mask=attention_mask
            ).logits
            correct += (logits.argmax(dim=1) == labels).sum().item()
            total += labels.size(0)
    return correct / total if total else 0.0


def main():
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        get_linear_schedule_with_warmup,
    )

    set_seed()
    frame, disease2id = load_training_data()
    train_frame, validation_frame, singleton_labels = build_train_validation_split(
        frame
    )

    if singleton_labels:
        print(
            f"WARNING: {len(singleton_labels)} singleton disease classes remain "
            "in training but are excluded from validation because they have only "
            "one sample."
        )

    tokenizer = AutoTokenizer.from_pretrained(BIOBERT_MODEL)
    train_loader = DataLoader(
        SymptomDataset(train_frame, tokenizer, disease2id),
        batch_size=BATCH_SIZE,
        shuffle=True,
    )
    validation_loader = DataLoader(
        SymptomDataset(validation_frame, tokenizer, disease2id),
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AutoModelForSequenceClassification.from_pretrained(
        BIOBERT_MODEL,
        num_labels=len(disease2id),
        label2id=disease2id,
        id2label={value: key for key, value in disease2id.items()},
    ).to(device)

    optimizer = torch.optim.AdamW(
        model.parameters(), lr=LEARNING_RATE, weight_decay=0.01
    )
    total_steps = len(train_loader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=max(1, total_steps // 10),
        num_training_steps=total_steps,
    )

    best_accuracy = -1.0
    output_dir = SAVED_WEIGHTS_DIR / "disease_predictor"
    temporary_dir = output_dir.with_name(output_dir.name + ".tmp")
    output_dir.parent.mkdir(parents=True, exist_ok=True)

    print(
        f"Training BioBERT: {len(frame)} rows, {len(disease2id)} classes, "
        f"{len(train_frame)} train / {len(validation_frame)} validation on {device}"
    )

    try:
        for epoch in range(EPOCHS):
            model.train()
            total_loss = 0.0
            for batch in train_loader:
                batch = {key: value.to(device) for key, value in batch.items()}
                optimizer.zero_grad(set_to_none=True)
                loss = model(**batch).loss
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                total_loss += float(loss.item())

            accuracy = evaluate(model, validation_loader, device)
            average_loss = total_loss / max(1, len(train_loader))
            print(
                f"Epoch {epoch + 1}/{EPOCHS} — loss: {average_loss:.4f} — "
                f"validation accuracy: {accuracy:.4%}"
            )

            if accuracy > best_accuracy:
                best_accuracy = accuracy
                if temporary_dir.exists():
                    shutil.rmtree(temporary_dir)
                temporary_dir.mkdir(parents=True)
                model.save_pretrained(temporary_dir)
                tokenizer.save_pretrained(temporary_dir)
                with (temporary_dir / "disease2id.json").open(
                    "w", encoding="utf-8"
                ) as file:
                    json.dump(disease2id, file, indent=2, ensure_ascii=False)
                if output_dir.exists():
                    shutil.rmtree(output_dir)
                temporary_dir.rename(output_dir)
                print(
                    f"Saved best BioBERT artifacts ({best_accuracy:.4%}) "
                    f"to {output_dir}"
                )
    finally:
        if temporary_dir.exists():
            shutil.rmtree(temporary_dir)

    print(f"Training complete. Best validation accuracy: {best_accuracy:.4%}")


if __name__ == "__main__":
    main()
