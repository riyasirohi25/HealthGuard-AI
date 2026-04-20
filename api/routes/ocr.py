from fastapi import APIRouter

router = APIRouter()

@router.post("/ocr")
def ocr():
    return {"text": "dummy OCR"}