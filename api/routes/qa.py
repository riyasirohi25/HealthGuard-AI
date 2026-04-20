from fastapi import APIRouter

router = APIRouter()

@router.post("/qa")
def qa():
    return {"answer": "dummy answer"}
