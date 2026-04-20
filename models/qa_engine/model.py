# models/qa_engine/model.py

import json
import numpy as np
from models.base_model import BaseHealthModel, ModelInput, ModelOutput
from config.config import CLEANED_QA, EMBEDDING_MODEL, TOP_K_RESULTS


class QAEngineModel(BaseHealthModel):

    def __init__(self):
        super().__init__()
        self.index   = None
        self.records = []
        self.embedder = None

    def load(self):
        try:
            import faiss
            from sentence_transformers import SentenceTransformer

            index_path   = CLEANED_QA / "qa_faiss.index"
            records_path = CLEANED_QA / "qa_records.jsonl"

            if not index_path.exists() or not records_path.exists():
                print("FAISS index not found — run build_faiss_index.py first")
                return

            self.index = faiss.read_index(str(index_path))
            self.records = []
            with open(records_path) as f:
                for line in f:
                    self.records.append(json.loads(line))

            self.embedder = SentenceTransformer(EMBEDDING_MODEL)
            self.is_ready = True
            print(f"QA engine loaded — {len(self.records)} records indexed")

        except Exception as e:
            print(f"QA engine load failed: {e}")

    def predict(self, input: ModelInput) -> ModelOutput:
        query_vec = self.embedder.encode(
            [input.text], normalize_embeddings=True
        )
        distances, indices = self.index.search(
            np.array(query_vec).astype("float32"), TOP_K_RESULTS
        )

        retrieved = []
        for idx in indices[0]:
            if idx < len(self.records):
                retrieved.append(self.records[idx])

        if not retrieved:
            return ModelOutput(
                result={"question": input.text, "retrieved_chunks": 0},
                confidence=0.0,
                explanation="No relevant answer found in knowledge base"
            )

        best    = retrieved[0]
        answer  = best.get("answer", "No answer available")
        sources = [r.get("source", "medical_kb") for r in retrieved]

        return ModelOutput(
            result={
                "question":        input.text,
                "retrieved_chunks": len(retrieved),
                "sources_used":    sources
            },
            confidence=round(float(1 - distances[0][0]), 3),
            explanation=answer,
            sources=list(set(sources))
        )