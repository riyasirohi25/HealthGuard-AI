from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import disease, lab, qa, ocr

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

@app.get("/")
def root():
    return {"status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}