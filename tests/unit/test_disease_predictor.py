import json
import sys
import types
from types import SimpleNamespace

import pytest
import torch

from models.disease_predictor.model import DiseasePredictorModel


def _install_fake_transformers(monkeypatch):
    class FakeConfig:
        def __init__(self):
            self.model_type = "bert"
            self.hidden_size = 768
            self.vocab_size = 28996
            self.num_labels = 2
            self.label2id = {}
            self.id2label = {}

    class FakeModel(torch.nn.Module):
        def __init__(self, config):
            super().__init__()
            self.config = config
            self.classifier = torch.nn.Linear(768, config.num_labels)

        def forward(self, input_ids, attention_mask=None):
            logits = torch.zeros(
                input_ids.shape[0], self.config.num_labels, device=input_ids.device
            )
            logits[:, 7] = 10.0
            return SimpleNamespace(logits=logits)

    class FakeTokenizer:
        def __len__(self):
            return 28996

        def __call__(self, text, **kwargs):
            return {
                "input_ids": torch.tensor([[1, 2, 3]], dtype=torch.long),
                "attention_mask": torch.tensor([[1, 1, 1]], dtype=torch.long),
            }

    fake = types.ModuleType("transformers")
    fake.AutoConfig = SimpleNamespace(
        from_pretrained=lambda *args, **kwargs: FakeConfig()
    )
    fake.AutoModelForSequenceClassification = SimpleNamespace(
        from_config=lambda config: FakeModel(config),
        from_pretrained=lambda *args, **kwargs: FakeModel(FakeConfig()),
    )
    fake.AutoTokenizer = SimpleNamespace(
        from_pretrained=lambda *args, **kwargs: FakeTokenizer()
    )
    monkeypatch.setitem(sys.modules, "transformers", fake)
    return FakeModel


def _write_773_mapping(path):
    mapping = {f"disease-{index:03d}": index for index in range(773)}
    path.write_text(json.dumps(mapping), encoding="utf-8")
    return mapping


def test_model_not_ready_without_checkpoint_or_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr(
        DiseasePredictorModel, "artifact_dir", property(lambda self: tmp_path / "model")
    )
    monkeypatch.setattr(
        DiseasePredictorModel, "checkpoint_path", property(lambda self: tmp_path / "missing.pt")
    )
    monkeypatch.setattr(
        DiseasePredictorModel, "mapping_path", property(lambda self: tmp_path / "missing.json")
    )

    predictor = DiseasePredictorModel()
    predictor.load()

    assert predictor.is_ready is False
    assert predictor.model is None


def test_rejects_non_contiguous_label_ids(tmp_path):
    path = tmp_path / "disease2id.json"
    path.write_text(json.dumps({"condition-a": 0, "condition-b": 2}), encoding="utf-8")

    with pytest.raises(ValueError, match="contiguous"):
        DiseasePredictorModel._read_label_mapping(path)


def test_loads_773_class_kaggle_checkpoint_strictly_and_predicts(
    tmp_path, monkeypatch
):
    fake_model_class = _install_fake_transformers(monkeypatch)
    mapping_path = tmp_path / "disease2id.json"
    checkpoint_path = tmp_path / "disease_predictor_773.pt"
    mapping = _write_773_mapping(mapping_path)

    config = SimpleNamespace(
        model_type="bert",
        hidden_size=768,
        vocab_size=28996,
        num_labels=773,
        label2id=mapping,
        id2label={index: name for name, index in mapping.items()},
    )
    saved_state = fake_model_class(config).state_dict()
    torch.save(saved_state, checkpoint_path)

    monkeypatch.setattr(
        DiseasePredictorModel,
        "artifact_dir",
        property(lambda self: tmp_path / "self-contained-model"),
    )
    monkeypatch.setattr(
        DiseasePredictorModel,
        "mapping_path",
        property(lambda self: mapping_path),
    )
    monkeypatch.setattr(
        DiseasePredictorModel,
        "checkpoint_path",
        property(lambda self: checkpoint_path),
    )

    predictor = DiseasePredictorModel()
    predictor.load()

    assert predictor.is_ready is True
    assert predictor.num_labels == 773
    assert predictor.model.classifier.out_features == 773

    from models.base_model import ModelInput

    result = predictor.predict(ModelInput(text="fever, headache, cough"))
    assert len(result.result["diseases"]) == 3
    assert result.result["diseases"][0]["name"] == "disease-007"
    assert result.result["symptom_count"] == 3


def test_rejects_wrong_mapping_count_before_loading_transformers(
    tmp_path, monkeypatch
):
    mapping_path = tmp_path / "disease2id.json"
    mapping_path.write_text(
        json.dumps({"condition-a": 0, "condition-b": 1}),
        encoding="utf-8",
    )
    checkpoint_path = tmp_path / "disease_predictor_773.pt"
    checkpoint_path.write_bytes(b"not loaded")

    monkeypatch.setattr(
        DiseasePredictorModel,
        "artifact_dir",
        property(lambda self: tmp_path / "self-contained-model"),
    )
    monkeypatch.setattr(
        DiseasePredictorModel,
        "mapping_path",
        property(lambda self: mapping_path),
    )
    monkeypatch.setattr(
        DiseasePredictorModel,
        "checkpoint_path",
        property(lambda self: checkpoint_path),
    )

    predictor = DiseasePredictorModel()
    predictor.load()

    assert predictor.is_ready is False
    assert predictor.model is None
