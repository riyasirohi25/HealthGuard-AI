# core/orchestrator.py

from llm.ollama_client import OllamaClient
from models.disease_predictor.model import DiseasePredictorModel
from models.lab_analyzer.model import LabAnalyzerModel
from models.qa_engine.model import QAEngineModel
from models.base_model import ModelInput


class HealthOrchestrator:

    def __init__(self):
        print("Loading HealthGuard AI orchestrator...")
        self.llm = OllamaClient()

        # Check Ollama is running
        if not self.llm.is_running():
            print("WARNING: Ollama not running. Start it with: ollama serve")

        # Load all models
        print("Loading Disease Predictor...")
        self.disease_model = DiseasePredictorModel()
        self.disease_model.load()

        print("Loading Lab Analyzer...")
        self.lab_model = LabAnalyzerModel()
        self.lab_model.load()

        print("Loading QA Engine...")
        self.qa_model = QAEngineModel()
        self.qa_model.load()

        print("All modules loaded.")

    def handle(self, user_message: str) -> dict:
        # Step 1 — extract intent using LLM
        intent = self.llm.extract_intent(user_message)
        module = intent.get("module", "general")

        # Step 2 — route to correct model
        if module == "disease_predictor":
            symptoms = intent.get("symptoms", [])
            symptoms_text = ", ".join(symptoms) if symptoms else user_message

            if self.disease_model.is_ready:
                model_input  = ModelInput(text=symptoms_text)
                model_output = self.disease_model.safe_predict(model_input)
                response     = self.llm.format_disease_result(
                    model_output.result, user_message
                )
                return {
                    "response":    response,
                    "module_used": "Disease Predictor",
                    "raw_result":  model_output.result,
                    "confidence":  model_output.confidence
                }
            else:
                response = self.llm.chat(
                    f"User has these symptoms: {user_message}. "
                    f"Give a general response but say the prediction model is still loading."
                )
                return {
                    "response":    response,
                    "module_used": "General Assistant (model loading)",
                    "raw_result":  {},
                    "confidence":  0.0
                }

        elif module == "lab_analyzer":
            model_input = ModelInput(
                text=user_message,
                metadata={
                    "test_name": intent.get("lab_test", ""),
                    "value":     intent.get("lab_value", 0),
                    "sex":       intent.get("lab_sex")
                }
            )

            if self.lab_model.is_ready:
                model_output = self.lab_model.safe_predict(model_input)
                response     = self.llm.format_lab_result(
                    model_output.result, user_message
                )
                return {
                    "response":    response,
                    "module_used": "Lab Analyzer",
                    "raw_result":  model_output.result,
                    "confidence":  model_output.confidence
                }
            else:
                response = self.llm.chat(user_message)
                return {
                    "response":    response,
                    "module_used": "General Assistant (model loading)",
                    "raw_result":  {},
                    "confidence":  0.0
                }

        elif module == "qa_engine":
            if self.qa_model.is_ready:
                model_input  = ModelInput(text=user_message)
                model_output = self.qa_model.safe_predict(model_input)
                response     = self.llm.format_qa_result(
                    model_output.explanation, user_message
                )
                return {
                    "response":    response,
                    "module_used": "Medical Q&A",
                    "raw_result":  model_output.result,
                    "confidence":  model_output.confidence
                }
            else:
                response = self.llm.chat(user_message)
                return {
                    "response":    response,
                    "module_used": "General Assistant",
                    "raw_result":  {},
                    "confidence":  0.0
                }

        else:
            # General conversation — LLM handles directly
            response = self.llm.chat(user_message)
            return {
                "response":    response,
                "module_used": "General Assistant",
                "raw_result":  {},
                "confidence":  1.0
            }

    def reset_conversation(self):
        self.llm.reset()

    def get_module_status(self) -> dict:
        return {
            "ollama_llm":       "running" if self.llm.is_running() else "not running",
            "disease_predictor": "ready" if self.disease_model.is_ready else "not loaded",
            "lab_analyzer":      "ready" if self.lab_model.is_ready else "not loaded",
            "qa_engine":         "ready" if self.qa_model.is_ready else "not loaded"
        }