# 🏥 HealthGuard AI — Intelligent Medical Assistant System

🎥 [Watch Demo Video](https://youtu.be/fx8s1pgH0Mw)

An intelligent medical AI system that helps users understand symptoms, interpret lab reports, read prescriptions, and get answers to medical questions — all in one place.

---

## 📸 Platform Preview

![Dashboard](images/dashboard.png)

HealthGuard AI combines OCR, NLP, Retrieval-Augmented Generation (RAG), disease prediction, and local LLM orchestration into a unified healthcare intelligence platform designed to simplify complex medical information into explainable and accessible insights.

---

## 🚀 Features

* 🤒 **Disease Predictor** — Ranks possible conditions from symptoms using a fine-tuned BioBERT classifier; supported classes come from the exact training dataset and saved label mapping
* 🧪 **Lab Analyzer** — Interprets blood test results and flags abnormal values with explanations
* 💊 **Prescription Reader** — Reads handwritten and printed prescriptions using EasyOCR and summarizes them in simple language
* ❓ **Medical Q&A** — Answers health questions using a FAISS-indexed medical knowledge base
* 🤖 **LLM Integration** — Uses Ollama (phi3:mini) locally for natural language responses

---

## 🧠 AI Feature Demonstrations

### 🤒 Disease Prediction Input

![Disease Prediction Input](images/disease_prediction_input.png)

### ✅ Disease Prediction Output

![Disease Prediction Output](images/disease_prediction_output.png)

### 🧾 OCR-Based Medical Report Analysis

![Medical QA](images/qa_analysis.png)

### ❓ AI Medical Question Answering

![OCR Analysis](images/ocr_analysis.png)

### ⚙️ FastAPI Swagger Backend Interface

![Swagger UI](images/swagger_interface.png)

---

## 🧩 System Overview

HealthGuard AI follows a modular AI architecture consisting of:

* **Frontend Layer** — React + Vite interface for user interaction
* **Backend Layer** — FastAPI-powered API orchestration
* **AI Inference Layer** — BioBERT, Sentence Transformers, OCR pipelines, and local LLM inference
* **Retrieval Layer** — FAISS-powered medical knowledge retrieval
* **LLM Layer** — Ollama-hosted lightweight language models for contextual responses

The platform is designed with a strong focus on:

* Explainable AI
* Privacy-focused local inference
* Healthcare accessibility
* Modular AI orchestration

---

## 🧠 BioBERT Model Artifacts — 773 Classes

The recovered Kaggle disease-prediction checkpoint is stored locally at:

```text
models/saved_weights/disease_predictor_773.pt
```

Its matching label map is:

```text
data/cleaned/symptom_disease/disease2id.json
```

The checkpoint is a fine-tuned BioBERT state dictionary with a 773-output classifier head. The loader uses strict state-dictionary loading and refuses to start if the tensor names/shapes or label count do not match.

The base BioBERT model and tokenizer must also be available. By default, the project uses `dmis-lab/biobert-v1.1`. For an offline/local Hugging Face snapshot, set:

```bash
export HEALTHGUARD_BIOBERT_BASE="/path/to/biobert-v1.1/snapshot"
```

The supplied Kaggle CSV contains 189,647 rows and 773 disease classes. Its `disease_id` values were checked against the repository's canonical alphabetical 773-class map. Keep the dataset and map from the same Kaggle dataset version.

The smaller 4,920-row raw symptom tables are a separate legacy 41-class source. Running `scripts/data_cleaning/clean_symptoms.py` writes its output to `data/cleaned/symptom_disease_legacy_41/`; it does not overwrite the 773-class mapping.

---
 
## 🛠️ Tech Stack

| Layer         | Technology                       |
| ------------- | -------------------------------- |
| Frontend      | React + Vite                     |
| Backend       | FastAPI (Python)                 |
| Disease Model | BioBERT (fine-tuned)             |
| OCR           | EasyOCR                          |
| LLM           | Ollama — phi3:mini               |
| QA Engine     | FAISS + SentenceTransformers     |
| Lab Analyzer  | Rule-based with reference ranges |

---

## ⚙️ Setup & Installation

### Prerequisites

* Python 3.10+
* Node.js 18+
* [Ollama](https://ollama.com) installed

---

### 1. Clone the Repository

```bash
git clone https://github.com/riyasirohi25/HealthGuard-AI.git
cd healthguard-ai
```

---

### 2. Create Virtual Environment

```bash
python -m venv venv
```

#### Windows

```bash
venv\Scripts\activate
```

#### Mac/Linux

```bash
source venv/bin/activate
```

---

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure the Recovered 773-Class BioBERT Model

Place the recovered checkpoint at:

```text
models/saved_weights/disease_predictor_773.pt
```

Keep the matching tracked mapping at:

```text
data/cleaned/symptom_disease/disease2id.json
```

If the BioBERT base model is already cached locally and the machine has no Hugging Face Hub access, point the project at that snapshot before starting the backend:

```bash
export HEALTHGUARD_BIOBERT_BASE="/path/to/biobert-v1.1/snapshot"
```

The model loader validates the 773-class mapping and strictly loads the recovered checkpoint into the configured BioBERT architecture. It does not retrain the model.

The fine-tuning script is available for a future training run using the 773-class cleaned CSV at `data/cleaned/symptom_disease/symptoms_diseases_clean.csv`. It validates any existing `disease_id` column against the canonical map and keeps single-example classes in training only (they cannot also appear in validation without data leakage).

**Do not run the legacy 41-class cleaner to recreate the 773-class training data.** That cleaner writes to `data/cleaned/symptom_disease_legacy_41/` and uses a separate source dataset.

### 5. Pull Ollama Model

```bash
ollama pull phi3:mini
```

---

### 6. Install Frontend Dependencies

```bash
cd hg-frontend
npm install
cd ..
```

---

## ▶️ Running the Project

### Terminal 1 — Start Ollama

```bash
ollama serve
```

---

### Terminal 2 — Start Backend

```bash
python -m uvicorn api.main:app --reload
```

---

### Terminal 3 — Start Frontend

```bash
cd hg-frontend
npm run dev
```

Then open:

```bash
http://localhost:5173
```

---

## 🎬 Live Demo Preview

### 🏥 Frontend Dashboard

![Frontend Dashboard](images/dashboard.png)

### 📄 Sample OCR Medical Report

![Demo Report](images/demo_report.png)

---

## 🧪 Example Inputs to Test

### Symptoms

```text
I have fever, sore throat, cough and runny nose since 3 days
```

### Lab Test

```text
my hemoglobin is 9.5
```

```text
my glucose_fasting is 280
```

### Medical Question

```text
What are common causes of fatigue?
```

### Prescription

Upload any prescription image via the chat interface.

---

## 📁 Project Structure

```bash
healthguard-ai/
├── api/              # FastAPI routes and main app
├── config/           # Configuration files
├── core/             # Orchestrator logic
├── hg-frontend/      # React frontend
├── llm/              # Ollama client
├── models/           # ML models (BioBERT, Lab Analyzer, QA Engine)
├── notebooks/        # Training notebooks
├── scripts/          # Data cleaning and preprocessing scripts
├── tests/            # Unit tests
└── requirements.txt
```

---

## 📓 Model Training

The recovered Kaggle BioBERT checkpoint has **773 output classes**. The supplied Kaggle cleaned dataset contains **189,647 rows across 773 diseases**. Its label IDs are contiguous from 0 to 772, unique per disease, and consistent with the canonical alphabetical `disease2id.json` mapping.

The repository notebook also contains an older 41-class experiment (304 cleaned rows). That notebook output describes a different, smaller dataset and must not be used as the label map for the recovered 773-class checkpoint.

For future fine-tuning, run `python scripts/training/train_disease_predictor.py` only after placing the matching 773-class cleaned CSV in the configured data directory. Validation omits singleton classes while retaining them in training.

---
 
## 🌍 Real-World Impact

HealthGuard AI is designed to improve healthcare accessibility by simplifying complex medical information through AI-powered analysis and explainable healthcare intelligence.

The platform aims to support:

* Early health awareness
* Simplified medical understanding
* Accessible healthcare assistance
* Privacy-focused local AI inference
* AI-assisted healthcare guidance
* Healthcare support for underserved communities

---

## ⚠️ Disclaimer

HealthGuard AI is for informational purposes only. It is **not a substitute for professional medical advice**. Always consult a qualified physician for diagnosis and treatment.

---

## 👥 Team & Contributions

This project was developed collaboratively as part of a team.

### 👩‍💻 My Contributions (Riya Sirohi)

* Fine-tuned BioBERT disease classification model on 770+ disease categories.
* Designed and implemented the FAISS-based retrieval pipeline for medical question answering.
* Built OCR-based prescription analysis workflow using EasyOCR.
* Developed the local LLM orchestration layer using Ollama and phi3.
* Implemented FastAPI backend services and AI model integration.

---

## 🤝 Original Repository

Original Repository:
https://github.com/Shagunnn25/healthguard-ai

---

## 👩‍💻 Built By

* Chahak Porwal
* Mumal Singh
* Riya Sirohi
* Shagun Mogha

— HealthGuard AI Project

---

## 🎥 Project Demonstration

Watch Full Demo:
https://youtu.be/fx8s1pgH0Mw
