from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os

from api.routes import disease, lab, qa, ocr
from core.orchestrator import HealthOrchestrator
from llm.ollama_client import OllamaClient

app = FastAPI(title="HealthGuard AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(disease.router)
app.include_router(lab.router)
app.include_router(qa.router)
app.include_router(ocr.router)

# ── Initialize orchestrator and LLM once ──────────────────
_orchestrator = HealthOrchestrator()
_llm = OllamaClient()

# ── Initialize EasyOCR once at startup ────────────────────
import easyocr
print("Loading EasyOCR model...")
_ocr_reader = easyocr.Reader(['en', 'hi'], gpu=False)
print("EasyOCR ready")

# ── Chat endpoint ─────────────────────────────────
class ChatRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {"status": "running", "message": "HealthGuard AI is live"}

@app.get("/health")
def health():
    return {
        "status": "ok",
        "modules": {
            "disease_predictor": "ready",
            "lab_analyzer":      "ready",
            "medical_qa":        "ready",
            "ocr":               "ready"
        }
    }

@app.post("/reset")
def reset():
    return {"status": "ok"}

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        result = _orchestrator.handle(req.message)
        return {
            "response":    result.get("response", ""),
            "module_used": result.get("module_used", "General Assistant"),
            "confidence":  result.get("confidence", 0.0),
            "raw_result":  result.get("raw_result", {}),
            "disclaimer":  "Not a substitute for professional medical advice."
        }
    except Exception as e:
        return {
            "response":    f"Error processing your request: {str(e)}",
            "module_used": "Error",
            "confidence":  0.0,
            "raw_result":  {},
            "disclaimer":  "Not a substitute for professional medical advice."
        }

@app.post("/chat/upload")
async def chat_with_file(
    message: str = Form(default=""),
    file: UploadFile = File(...)
):
    try:
        file_bytes = await file.read()
        filename   = file.filename.lower()
        extracted_text = ""

        # ── PDF ──────────────────────────────────────
        if filename.endswith(".pdf"):
            try:
                import pdfplumber
                import io
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    extracted_text = "\n".join(
                        page.extract_text() or "" for page in pdf.pages
                    )
            except Exception as ex:
                extracted_text = f"[Could not extract PDF text: {str(ex)}]"

        # ── Image — EasyOCR ───────────────────────────
        elif filename.endswith((".png", ".jpg", ".jpeg", ".webp")):
            try:
                import numpy as np
                from PIL import Image
                import io

                image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
                image_np = np.array(image)

                results = _ocr_reader.readtext(image_np)

                # Extract text with confidence filter
                lines = []
                for (bbox, text, confidence) in results:
                    if confidence > 0.1:  # include even low confidence for handwriting
                        lines.append(text)

                extracted_text = "\n".join(lines)

                if not extracted_text.strip():
                    extracted_text = "[Could not extract text — image may be unclear]"

            except Exception as ex:
                extracted_text = f"[EasyOCR error: {str(ex)}]"

        # ── Plain text / CSV ─────────────────────────
        elif filename.endswith((".txt", ".csv")):
            extracted_text = file_bytes.decode("utf-8", errors="ignore")

        # ── Word doc ─────────────────────────────────
        elif filename.endswith((".doc", ".docx")):
            try:
                import docx
                import io
                doc = docx.Document(io.BytesIO(file_bytes))
                extracted_text = "\n".join(p.text for p in doc.paragraphs)
            except Exception as ex:
                extracted_text = f"[Could not extract Word document text: {str(ex)}]"

        else:
            extracted_text = "[Unsupported file type]"

        # ── If extraction failed ──────────────────────
        if extracted_text.startswith("["):
            return {
                "response": (
                    f"Could not read the document.\n\n{extracted_text}\n\n"
                    f"Please make sure the image is clear and well-lit."
                ),
                "module_used": "OCR Reader",
                "confidence": 0.0,
                "raw_result": {},
                "disclaimer": "Not a substitute for professional medical advice."
            }

        # ── Clean extracted text ──────────────────────
        lines = [l.strip() for l in extracted_text.split('\n') if l.strip()]
        clean_text = "\n".join(lines[:50])

        user_question = message.strip() or "explain this prescription"

        # ── Send to Mistral ───────────────────────────
        direct_prompt = (
            f"You are a medical assistant. A patient uploaded their prescription. "
            f"The text below was scanned from it using OCR. "
            f"Read it carefully and explain in simple English:\n"
            f"- What condition the patient likely has based on the medicines prescribed\n"
            f"- Each medicine name and what it is commonly used for\n"
            f"- When and how to take each medicine (morning/night/before food etc)\n"
            f"- Any special instructions or follow up mentioned\n\n"
            f"PRESCRIPTION TEXT:\n{clean_text}\n\n"
            f"Give a clear, simple, friendly explanation a non-medical person can understand."
        )

        response_text = _llm.chat(direct_prompt)

        if not response_text or response_text.startswith("LLM error"):
            response_text = (
                f"Here is what was read from your prescription:\n\n"
                + "\n".join(lines[:40])
                + "\n\nPlease show this to your pharmacist for a detailed explanation."
            )

        return {
            "response":    response_text,
            "module_used": "EasyOCR + Prescription Reader",
            "confidence":  0.95,
            "raw_result":  {"extracted_text": extracted_text[:500]},
            "disclaimer":  "Not a substitute for professional medical advice."
        }

    except Exception as e:
        return {
            "response":    f"Error processing file: {str(e)}",
            "module_used": "Error",
            "confidence":  0.0,
            "raw_result":  {},
            "disclaimer":  "Not a substitute for professional medical advice."
        }