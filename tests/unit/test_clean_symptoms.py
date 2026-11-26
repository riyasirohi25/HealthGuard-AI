import pandas as pd

from scripts.data_cleaning.clean_symptoms import clean_symptom_files


def test_cleaning_joins_disease_and_symptom_aliases(tmp_path):
    pd.DataFrame(
        {
            "Disease": [
                "Dimorphic hemmorhoids(piles)",
                "Dimorphic hemmorhoids(piles)",
                "Acne",
                "Acne",
            ],
            "Symptom_1": [
                "foul_smell_of_urine",
                "itching",
                "itching",
                "foul_smell_of_urine",
            ],
        }
    ).to_csv(tmp_path / "dataset.csv", index=False)

    pd.DataFrame(
        {
            "Disease": ["Dimorphic hemorrhoids(piles)", "Acne"],
            "Description": ["Description for piles", "Description for acne"],
        }
    ).to_csv(tmp_path / "symptom_Description.csv", index=False)

    pd.DataFrame(
        {
            "Disease": ["Dimorphic hemorrhoids(piles)", "Acne"],
            "Precaution_1": ["Consult a clinician", "Keep skin clean"],
        }
    ).to_csv(tmp_path / "symptom_precaution.csv", index=False)

    pd.DataFrame(
        {
            "Symptom": ["foul_smell_ofurine", "itching"],
            "weight": [5, 1],
        }
    ).to_csv(tmp_path / "Symptom-severity.csv", index=False)

    cleaned, disease2id, severity_lookup = clean_symptom_files(tmp_path)

    assert len(cleaned) == 4
    assert disease2id == {"acne": 0, "dimorphic hemmorhoidspiles": 1}
    assert cleaned["description"].notna().all()
    assert cleaned["precautions"].notna().all()
    assert severity_lookup["foul smell of urine"] == 5.0
    assert (cleaned["avg_severity"] > 0).all()


def test_cleaning_reports_conflicting_duplicate_severity_values(tmp_path, capsys):
    pd.DataFrame(
        {"Disease": ["Acne"], "Symptom_1": ["itching"]}
    ).to_csv(tmp_path / "dataset.csv", index=False)
    pd.DataFrame(
        {"Disease": ["Acne"], "Description": ["Description"]}
    ).to_csv(tmp_path / "symptom_Description.csv", index=False)
    pd.DataFrame(
        {"Disease": ["Acne"], "Precaution_1": ["Precaution"]}
    ).to_csv(tmp_path / "symptom_precaution.csv", index=False)
    pd.DataFrame(
        {
            "Symptom": ["itching", "fluid_overload", "fluid_overload"],
            "weight": [1, 6, 4],
        }
    ).to_csv(tmp_path / "Symptom-severity.csv", index=False)

    cleaned, _, severity_lookup = clean_symptom_files(tmp_path)
    captured = capsys.readouterr()

    assert "conflicting duplicate symptom severity values" in captured.out
    assert severity_lookup["fluid overload"] == 4.0
    assert cleaned.loc[0, "avg_severity"] == 1.0
