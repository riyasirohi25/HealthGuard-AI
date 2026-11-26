"""Clean the symptom/disease source tables used by the BioBERT trainer."""
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

from config.config import RAW_SYMPTOM, LEGACY_CLEANED_SYMPTOM


# Source datasets contain a few inconsistent spellings. These aliases are used
# only for joins; the disease names used as classifier labels remain unchanged.
DISEASE_JOIN_ALIASES = {
    "dimorphic hemorrhoidspiles": "dimorphic hemmorhoidspiles",
}
SEVERITY_SYMPTOM_ALIASES = {
    "foul smell ofurine": "foul smell of urine",
}


def normalize_columns(frame):
    frame = frame.copy()
    frame.columns = [str(column).strip().lower().replace(" ", "_") for column in frame.columns]
    return frame


def clean_disease_name(name):
    if pd.isna(name):
        return None
    name = str(name).strip().lower()
    name = re.sub(r"[^a-z0-9 _-]", "", name)
    return re.sub(r"\s+", " ", name).strip()


def disease_join_key(name):
    cleaned = clean_disease_name(name)
    return DISEASE_JOIN_ALIASES.get(cleaned, cleaned)


def clean_symptom(symptom):
    if pd.isna(symptom):
        return None
    symptom = str(symptom).strip().lower().replace("_", " ")
    symptom = re.sub(r"\s+", " ", symptom).strip()
    return symptom or None


def severity_join_key(symptom):
    cleaned = clean_symptom(symptom)
    return SEVERITY_SYMPTOM_ALIASES.get(cleaned, cleaned)


def clean_symptom_files(raw_dir=RAW_SYMPTOM):
    """Return the cleaned frame, label mapping, and severity lookup.

    The function is side-effect free apart from reading its inputs, which makes
    the cleaning rules independently testable.
    """
    raw_dir = Path(raw_dir)
    df = normalize_columns(pd.read_csv(raw_dir / "dataset.csv"))
    df_desc = normalize_columns(pd.read_csv(raw_dir / "symptom_Description.csv"))
    df_prec = normalize_columns(pd.read_csv(raw_dir / "symptom_precaution.csv"))
    df_sev = normalize_columns(pd.read_csv(raw_dir / "Symptom-severity.csv"))

    required_dataset = {"disease"}
    required_description = {"disease", "description"}
    required_precaution = {"disease"}
    if not required_dataset.issubset(df.columns):
        raise ValueError("dataset.csv must contain a Disease column")
    if not required_description.issubset(df_desc.columns):
        raise ValueError("symptom_Description.csv must contain Disease and Description columns")
    if not required_precaution.issubset(df_prec.columns):
        raise ValueError("symptom_precaution.csv must contain a Disease column")
    if len(df_sev.columns) < 2:
        raise ValueError("Symptom-severity.csv must contain symptom and weight columns")

    df["disease"] = df["disease"].apply(clean_disease_name)
    df_desc["disease_key"] = df_desc["disease"].apply(disease_join_key)
    df_prec["disease_key"] = df_prec["disease"].apply(disease_join_key)
    df["disease_key"] = df["disease"].apply(disease_join_key)

    symptom_cols = [column for column in df.columns if column.startswith("symptom_")]
    if not symptom_cols:
        raise ValueError("dataset.csv must contain at least one Symptom_N column")
    for column in symptom_cols:
        df[column] = df[column].apply(clean_symptom)

    df = df.dropna(subset=["disease"]).drop_duplicates()

    severity_lookup = {}
    severity_values = defaultdict(set)
    for _, row in df_sev.iterrows():
        symptom_key = severity_join_key(row.iloc[0])
        if not symptom_key:
            continue
        try:
            weight = float(row.iloc[1])
        except (TypeError, ValueError):
            weight = 0.0
        severity_values[symptom_key].add(weight)
        # Preserve the source file's historical last-row-wins behavior, but
        # make conflicting duplicate weights visible instead of silent.
        severity_lookup[symptom_key] = weight

    conflicting_severity = {
        symptom: sorted(weights)
        for symptom, weights in severity_values.items()
        if len(weights) > 1
    }
    if conflicting_severity:
        print(
            "WARNING: conflicting duplicate symptom severity values; "
            f"using the last row for compatibility: {conflicting_severity}"
        )

    records = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Cleaning symptom rows"):
        symptoms = [
            row[column]
            for column in symptom_cols
            if pd.notna(row[column])
            and str(row[column]).strip().lower() not in {"", "nan", "none"}
        ]
        if not symptoms:
            continue
        severity_scores = [severity_lookup.get(symptom, 0.0) for symptom in symptoms]
        records.append(
            {
                "disease": row["disease"],
                "disease_key": row["disease_key"],
                "symptoms": symptoms,
                "symptoms_text": ", ".join(symptoms),
                "symptom_count": len(symptoms),
                "avg_severity": round(float(np.mean(severity_scores)), 3),
                "max_severity": max(severity_scores),
            }
        )

    df_clean = pd.DataFrame(records)
    description_columns = [
        column for column in df_desc.columns if column not in {"disease", "disease_key"}
    ]
    description_table = df_desc[["disease_key"] + description_columns].drop_duplicates(
        subset=["disease_key"]
    )
    df_clean = df_clean.merge(
        description_table, on="disease_key", how="left", validate="many_to_one"
    )

    precaution_columns = [
        column for column in df_prec.columns if column.startswith("precaution")
    ]
    if not precaution_columns:
        raise ValueError("symptom_precaution.csv must contain Precaution_N columns")
    df_prec["precautions"] = df_prec[precaution_columns].apply(
        lambda row: [
            str(value).strip()
            for value in row
            if pd.notna(value) and str(value).strip()
        ],
        axis=1,
    )
    precaution_table = df_prec[["disease_key", "precautions"]].drop_duplicates(
        subset=["disease_key"]
    )
    df_clean = df_clean.merge(
        precaution_table, on="disease_key", how="left", validate="many_to_one"
    )
    df_clean = df_clean.drop(columns=["disease_key"])

    missing_descriptions = sorted(
        df_clean.loc[df_clean["description"].isna(), "disease"].unique().tolist()
    )
    if missing_descriptions:
        print(f"WARNING: descriptions missing for diseases: {missing_descriptions}")

    all_symptoms = {
        symptom
        for symptoms in df_clean["symptoms"]
        for symptom in symptoms
    }
    missing_severity = sorted(all_symptoms.difference(severity_lookup))
    if missing_severity:
        print(
            "WARNING: symptoms without severity weights (defaulting to 0.0): "
            f"{missing_severity}"
        )

    disease_list = sorted(df_clean["disease"].unique())
    disease2id = {disease: index for index, disease in enumerate(disease_list)}
    df_clean["disease_id"] = df_clean["disease"].map(disease2id)

    return df_clean, disease2id, severity_lookup


def main():
    print(f"Reading original symptom dataset from: {RAW_SYMPTOM}")
    df_clean, disease2id, severity_lookup = clean_symptom_files(RAW_SYMPTOM)
    LEGACY_CLEANED_SYMPTOM.mkdir(parents=True, exist_ok=True)

    print(f"Final records: {len(df_clean)}")
    print(f"Unique diseases: {df_clean['disease'].nunique()}")
    print(
        "Samples per disease: "
        f"min={df_clean['disease'].value_counts().min()}, "
        f"max={df_clean['disease'].value_counts().max()}"
    )

    df_clean.to_csv(LEGACY_CLEANED_SYMPTOM / "symptoms_diseases_clean.csv", index=False)
    with (LEGACY_CLEANED_SYMPTOM / "disease2id.json").open("w", encoding="utf-8") as file:
        json.dump(disease2id, file, indent=2, ensure_ascii=False)
    with (LEGACY_CLEANED_SYMPTOM / "symptom_severity.json").open("w", encoding="utf-8") as file:
        json.dump(severity_lookup, file, indent=2, ensure_ascii=False)
    with (LEGACY_CLEANED_SYMPTOM / "all_symptoms.json").open("w", encoding="utf-8") as file:
        json.dump(sorted(severity_lookup.keys()), file, indent=2, ensure_ascii=False)

    print(f"Legacy 41-class cleaned files saved to: {LEGACY_CLEANED_SYMPTOM}")


if __name__ == "__main__":
    main()
