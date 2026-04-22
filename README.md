# 🏥 HealthGuard AI

An intelligent medical AI system that helps users understand symptoms, interpret lab reports, read prescriptions, and get answers to medical questions — all in one place.

---

## 🚀 Features

- 🤒 **Disease Predictor** — Detects possible conditions from symptoms using a fine-tuned BioBERT model trained on 770+ diseases
- 🧪 **Lab Analyzer** — Interprets blood test results and flags abnormal values with explanations
- 💊 **Prescription Reader** — Reads handwritten and printed prescriptions using EasyOCR and summarizes them in simple language
- ❓ **Medical Q&A** — Answers health questions using a FAISS-indexed medical knowledge base
- 🤖 **LLM Integration** — Uses Ollama (phi3:mini) locally for natural language responses

---

## 🧠 Model Weights

The trained BioBERT disease predictor model (~415MB) is hosted on Google Drive:

📥 **[Download disease_predictor.pt](https://drive.google.com/file/d/1DSAOwZ-t40kSIbiiog55peYYXJ6FTFtQ/view?usp=sharing)**

After downloading, place it here:
```
models/saved_weights/disease_predictor.pt
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite |
| Backend | FastAPI (Python) |
| Disease Model | BioBERT (fine-tuned) |
| OCR | EasyOCR |
| LLM | Ollama — phi3:mini |
| QA Engine | FAISS + SentenceTransformers |
| Lab Analyzer | Rule-based with reference ranges |

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.com) installed

### 1. Clone the repository
```bash
git clone https://github.com/Shagunnn25/healthguard-ai.git
cd healthguard-ai
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4. Download model weights
Download `disease_predictor.pt` from the link above and place it in:
```
models/saved_weights/disease_predictor.pt
```

### 5. Pull Ollama model
```bash
ollama pull phi3:mini
```

### 6. Install frontend dependencies
```bash
cd hg-frontend
npm install
cd ..
```

---

## ▶️ Running the Project

**Terminal 1 — Start Ollama:**
```bash
ollama serve
```

**Terminal 2 — Start Backend:**
```bash
cd healthguard-ai
python -m uvicorn api.main:app --reload
```

**Terminal 3 — Start Frontend:**
```bash
cd hg-frontend
npm run dev
```

Then open: **http://localhost:5173**

---

## 🧪 Example Inputs to Test

**Symptoms:**
```
I have fever, sore throat, cough and runny nose since 3 days
```

**Lab Test:**
```
my hemoglobin is 9.5
```
```
my glucose_fasting is 280
```

**Medical Question:**
```
What is diabetes and how is it treated?
```

**Prescription:** Upload any prescription image via the chat

---

## 📁 Project Structure

```
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

The disease predictor was trained on Kaggle using a T4 GPU due to local RAM constraints.
Training achieved ~81.6% validation accuracy over 5 epochs on 770+ disease classes.

---

## ⚠️ Disclaimer

HealthGuard AI is for informational purposes only. It is **not a substitute for professional medical advice**. Always consult a qualified physician for diagnosis and treatment.

---
## 👥 Team & Contributions

This project was developed collaboratively as part of a team.

### 👩‍💻 My Contributions (Riya Sirohi)
- Integrated LLM pipeline using Ollama (phi3:mini) for response generation
- Implemented backend orchestration using FastAPI
- Worked on lab test analyzer logic and response formatting
- Assisted in frontend-backend integration and testing
- Helped optimize the system for low-RAM environments


Original Repository:
https://github.com/riyasirohi25/HealthGuard-AI

---
## 👩‍💻 Built by

Chahak Porwal,
Mumal Singh,
Riya Sirohi,
Shagun Mogha

— HealthGuard AI Project
