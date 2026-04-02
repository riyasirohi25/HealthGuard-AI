# models/base_model.py

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class ModelInput:
    text: str
    metadata: dict = field(default_factory=dict)


@dataclass
class ModelOutput:
    result: Any
    confidence: float
    explanation: str
    sources: List[str] = field(default_factory=list)
    error: Optional[str] = None


class BaseHealthModel(ABC):
    """
    Every model in HealthGuard AI must follow this interface.
    This ensures Person 1 can connect any model to the API
    without knowing the internal details.
    """

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.is_ready = False

    @abstractmethod
    def load(self):
        """Load model weights from disk"""
        pass

    @abstractmethod
    def predict(self, input: ModelInput) -> ModelOutput:
        """Run inference on input"""
        pass

    def health_check(self) -> dict:
        """Returns model status — used by API /health endpoint"""
        return {
            "model": self.__class__.__name__,
            "loaded": self.is_ready,
            "status": "ready" if self.is_ready else "not loaded"
        }

    def safe_predict(self, input: ModelInput) -> ModelOutput:
        """
        Wrapper around predict that catches errors.
        API always calls this instead of predict directly.
        """
        if not self.is_ready:
            return ModelOutput(
                result={},
                confidence=0.0,
                explanation="Model not loaded yet",
                error="Model not initialized"
            )
        try:
            return self.predict(input)
        except Exception as e:
            return ModelOutput(
                result={},
                confidence=0.0,
                explanation="Prediction failed",
                error=str(e)
            )