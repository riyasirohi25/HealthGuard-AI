import pandas as pd
import pytest

from scripts.training.train_disease_predictor import (
    build_train_validation_split,
    load_training_data,
)


def test_training_data_builds_deterministic_mapping(tmp_path, monkeypatch):
    import scripts.training.train_disease_predictor as training

    csv_path = tmp_path / "symptoms_diseases_clean.csv"
    pd.DataFrame(
        {
            "disease": ["zeta", "alpha", "zeta", "alpha"],
            "symptoms_text": ["cough", "rash", "fever", "itching"],
            "disease_id": [1, 0, 1, 0],
        }
    ).to_csv(csv_path, index=False)
    monkeypatch.setattr(training, "CLEANED_SYMPTOM", tmp_path)

    frame, mapping = load_training_data()

    assert mapping == {"alpha": 0, "zeta": 1}
    assert frame["label"].tolist() == [1, 0, 1, 0]


def test_training_data_rejects_dataset_id_mapping_mismatch(tmp_path, monkeypatch):
    import scripts.training.train_disease_predictor as training

    csv_path = tmp_path / "symptoms_diseases_clean.csv"
    pd.DataFrame(
        {
            "disease": ["alpha", "beta"],
            "symptoms_text": ["rash", "cough"],
            "disease_id": [1, 0],
        }
    ).to_csv(csv_path, index=False)
    monkeypatch.setattr(training, "CLEANED_SYMPTOM", tmp_path)

    with pytest.raises(ValueError, match="do not match the alphabetical mapping"):
        load_training_data()


def test_singleton_classes_stay_in_training_and_are_omitted_from_validation():
    import pandas as pd

    frame = pd.DataFrame(
        {
            "disease": ["alpha", "alpha", "beta", "gamma", "gamma"],
            "label": [0, 0, 1, 2, 2],
        }
    )

    train, validation, singletons = build_train_validation_split(
        frame, validation_fraction=0.2, seed=42
    )

    assert set(train["label"]) == {0, 1, 2}
    assert set(validation["label"]) == {0, 2}
    assert singletons == [1]
    assert len(train) + len(validation) == len(frame)


def test_training_data_reports_missing_dataset(tmp_path, monkeypatch):
    import scripts.training.train_disease_predictor as training

    monkeypatch.setattr(training, "CLEANED_SYMPTOM", tmp_path)

    with pytest.raises(FileNotFoundError, match="Place the 773-class Kaggle CSV"):
        load_training_data()
