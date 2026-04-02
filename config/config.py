# config/config.py

from pathlib import Path

# ── Base Directories ──────────────────────────────────
BASE_DIR    = Path(__file__).parent.parent
DATA_DIR    = BASE_DIR / "data"
MODELS_DIR  = BASE_DIR / "models"
LOGS_DIR    = BASE_DIR / "logs"
SCRIPTS_DIR = BASE_DIR / "scripts"

# ── Data Subdirectories ───────────────────────────────
RAW_DATA     = DATA_DIR / "raw"
CLEANED_DATA = DATA_DIR / "cleaned"

RAW_SYMPTOM    = RAW_DATA / "symptom_disease"
RAW_MEDQUAD    = RAW_DATA / "medquad"
RAW_MEDQA      = RAW_DATA / "medqa_usmle"
RAW_MEDMCQA    = RAW_DATA / "medmcqa"
RAW_LAB        = RAW_DATA / "lab_values"
RAW_NCBI       = RAW_DATA / "ncbi"

CLEANED_SYMPTOM = CLEANED_DATA / "symptom_disease"
CLEANED_QA      = CLEANED_DATA / "qa_datasets"
CLEANED_LAB     = CLEANED_DATA / "lab_values"
CLEANED_NCBI    = CLEANED_DATA / "ncbi"

# ── Model Subdirectories ──────────────────────────────
DISEASE_MODEL_DIR  = MODELS_DIR / "disease_predictor"
LAB_MODEL_DIR      = MODELS_DIR / "lab_analyzer"
QA_MODEL_DIR       = MODELS_DIR / "qa_engine"
SUMMARIZER_DIR     = MODELS_DIR / "summarizer"
SAVED_WEIGHTS_DIR  = MODELS_DIR / "saved_weights"

# ── Pretrained Model Names (HuggingFace) ──────────────
BIOBERT_MODEL      = "dmis-lab/biobert-v1.1"
FLAN_T5_MODEL      = "google/flan-t5-base"
EMBEDDING_MODEL    = "sentence-transformers/all-MiniLM-L6-v2"

# ── API Settings ──────────────────────────────────────
API_HOST    = "0.0.0.0"
API_PORT    = 8000
API_VERSION = "0.1.0"
APP_NAME    = "HealthGuard AI"

# ── Model Settings ────────────────────────────────────
MAX_INPUT_LENGTH   = 512
MAX_OUTPUT_LENGTH  = 256
BATCH_SIZE         = 16
NUM_EPOCHS         = 5
LEARNING_RATE      = 2e-5
TOP_K_RESULTS      = 3

# ── Create all directories if they don't exist ────────
for directory in [
    DATA_DIR, MODELS_DIR, LOGS_DIR,
    RAW_DATA, CLEANED_DATA,
    RAW_SYMPTOM, RAW_MEDQUAD, RAW_MEDQA,
    RAW_MEDMCQA, RAW_LAB, RAW_NCBI,
    CLEANED_SYMPTOM, CLEANED_QA, CLEANED_LAB, CLEANED_NCBI,
    DISEASE_MODEL_DIR, LAB_MODEL_DIR,
    QA_MODEL_DIR, SUMMARIZER_DIR, SAVED_WEIGHTS_DIR
]:
    directory.mkdir(parents=True, exist_ok=True)