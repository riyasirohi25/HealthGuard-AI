from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/ocr")
async def extract_text(file: UploadFile = File(...)):
    return {
        "result": {"filename": file.filename, "extracted_text": ""},
        "confidence": 0.0,
        "explanation": "OCR module not yet connected",
        "disclaimer": "This is not a substitute for professional medical advice."
    }
