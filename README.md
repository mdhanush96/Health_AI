# 🏥 MyHealth AI – Intelligent Health Companion & Diagnostic Assistant

[![CI/CD](https://github.com/mdhanush96/Health_AI/actions/workflows/ci.yml/badge.svg)](https://github.com/mdhanush96/Health_AI/actions)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-green)](https://djangoproject.com)
[![React](https://img.shields.io/badge/React-18-61dafb)](https://reactjs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A full-stack, AI-powered healthcare assistant integrating Clinical NLP, Medical Report Understanding, Retrieval-Augmented Generation (RAG), and Personalized Recommendation Intelligence.

---

## 📋 Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [ML Pipeline](#ml-pipeline)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Testing](#testing)
- [Security & Compliance](#security--compliance)

---

## ✨ Features

| Feature | Technology | Description |
|---------|-----------|-------------|
| 🩺 Symptom Classification | ClinicalBERT | Multi-class NLP classification of symptoms |
| 📄 Report OCR | Tesseract + PyMuPDF | Extract text from PDF, images, CSV |
| 🤖 Report Summarization | T5-small / BART | AI-powered clinical summary generation |
| 🔍 RAG Responses | FAISS + SBERT | Grounded medical responses from knowledge base |
| 💊 Recommendations | Rule Engine | Personalized diet, exercise, medication guidance |
| 🚨 Emergency Detection | Pattern Matching | Multi-level severity assessment |
| 🔐 Authentication | JWT | Secure token-based user authentication |
| 📊 Health History | MySQL | Longitudinal health record storage |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│  Login │ Dashboard │ SymptomForm │ ReportUpload          │
│  SummaryView │ Recommendations │ EmergencyAlert          │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/HTTPS (JWT Auth)
┌──────────────────────▼──────────────────────────────────┐
│              Django REST API Gateway                      │
│                                                          │
│  /api/auth/    │ /api/symptom/  │ /api/report/           │
│  /api/recommend│ /api/emergency/│ /api/history/          │
└──────┬────────────────┬─────────────────┬───────────────┘
       │                │                 │
┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
│  ML Engine  │  │  RAG System │  │  Recommender │
│ ClinicalBERT│  │ FAISS+SBERT │  │   Engine     │
│ T5 Summarize│  │  Top-K=5    │  │  Per-Category│
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                 │
┌──────▼─────────────────────────────────▼──────────────┐
│                   MySQL Database                        │
│  users │ symptoms │ reports │ recommendations           │
│  emergency_alerts │ health_history                      │
└────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Backend | Django 4.2 + DRF | Secure, structured, scalable REST APIs |
| Frontend | React 18 | Component-based SPA with Context API |
| Database | MySQL 8.0 | Structured relational health data |
| OCR | Tesseract + PyMuPDF | Open-source, supports PDF/Image/CSV |
| Symptom NLP | ClinicalBERT | Pre-trained on clinical notes (MIMIC) |
| Summarization | T5-small / BART | GPU-friendly transformer summarization |
| Embeddings | all-MiniLM-L6-v2 | Efficient semantic encoding (SBERT) |
| Vector DB | FAISS | Academic-friendly, GPU-enabled search |
| Auth | JWT (SimpleJWT) | Stateless token-based authentication |
| Cloud | AWS EC2/RDS/S3 | HIPAA-eligible services |
| DevOps | Docker + GitHub Actions | Containerized CI/CD pipeline |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- MySQL 8.0+
- Tesseract OCR (`sudo apt install tesseract-ocr`)

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/mdhanush96/Health_AI.git
cd Health_AI

# Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your settings

# Start all services
docker-compose up --build

# Access the app
# Frontend: http://localhost:80
# Backend API: http://localhost:8000
# Admin: http://localhost:8000/admin
```

### Option 2: Manual Setup

```bash
# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your MySQL credentials

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Start backend server
python manage.py runserver
```

```bash
# Frontend setup (in a new terminal)
cd frontend
npm install
npm start
# App opens at http://localhost:3000
```

---

## 📡 API Reference

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | Register new user |
| `/api/auth/login/` | POST | Login (returns JWT tokens) |
| `/api/auth/logout/` | POST | Logout (blacklists refresh token) |
| `/api/auth/token/refresh/` | POST | Refresh access token |
| `/api/auth/profile/` | GET/PUT | View/update user profile |

### Core APIs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/symptom/` | POST | Symptom classification + RAG response |
| `/api/report/upload/` | POST | Upload PDF/Image/CSV medical report |
| `/api/report/analyze/` | POST | Summarize extracted report text |
| `/api/recommend/` | GET | Get personalized health recommendations |
| `/api/emergency/` | POST | Emergency severity detection |
| `/api/history/` | GET | Paginated health history |

### Example: Symptom Analysis

```bash
curl -X POST http://localhost:8000/api/symptom/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"symptom_text": "I have chest pain and shortness of breath for 2 hours"}'
```

**Response:**
```json
{
  "analysis_id": 42,
  "classification": "cardiovascular",
  "confidence_score": 0.87,
  "risk_level": "HIGH",
  "rag_response": "Chest pain with shortness of breath may indicate cardiac issues...",
  "sources": ["AHA Guidelines", "Clinical Guidelines"],
  "retrieved_context": "Chest pain can indicate cardiac issues..."
}
```

---

## 🤖 ML Pipeline

### Model Architecture

```
Input Text
    ↓
Preprocessing (lowercasing, normalization, ICD mapping)
    ↓
ClinicalBERT (Symptom Classification)
    ↓ ↘
    │   SBERT Embedding → FAISS Index Search (Top-K=5)
    │           ↓
    │   Retrieved Context
    │           ↓
    └→  T5 Generator → Grounded Response
```

### Fine-Tuning

#### ClinicalBERT Classifier
```bash
cd ml/models
python fine_tune_classifier.py \
    --dataset data/symptom_dataset.csv \
    --output_dir ./models/clinical_bert_classifier \
    --epochs 3 --batch_size 16 --lr 2e-5
```

| Hyperparameter | Value |
|---------------|-------|
| Epochs | 3 |
| Batch size | 16 |
| Learning rate | 2e-5 |
| Optimizer | AdamW |
| Max length | 256 |
| Loss | CrossEntropyLoss |

#### T5 Summarizer
```bash
python fine_tune_summarizer.py \
    --dataset data/reports_dataset.csv \
    --output_dir ./models/t5_summarizer \
    --epochs 5 --batch_size 8 --lr 3e-4
```

Evaluated using ROUGE-1, ROUGE-2, ROUGE-L metrics.

#### Build FAISS Index
```bash
cd ml/rag
python build_faiss_index.py \
    --knowledge_base ../data/knowledge_base.json \
    --output_dir ../../backend/ml_data \
    --model all-MiniLM-L6-v2
```

### GPU Optimization (RTX 2050 - 4GB VRAM)

| Model | VRAM Usage |
|-------|-----------|
| ClinicalBERT | ~1.2 GB |
| T5-small | ~1.8 GB |
| FAISS Index | ~500 MB |
| **Total** | **~3.5 GB** |

Enable FP16 mixed precision for ~50% VRAM reduction:
```python
model = model.half()  # FP16
```

---

## 📁 Project Structure

```
Health_AI/
├── backend/                    # Django REST API
│   ├── health_ai/             # Project settings & URLs
│   ├── users/                 # Authentication & profiles
│   ├── reports/               # Report upload & OCR
│   ├── ml_engine/             # ClinicalBERT + RAG
│   ├── recommendations/       # Health recommendation engine
│   ├── emergency/             # Emergency severity detection
│   ├── history/               # Health history tracking
│   ├── requirements.txt
│   └── tests.py               # Backend tests
│
├── frontend/                   # React.js SPA
│   └── src/
│       ├── App.js
│       ├── api.js             # Axios API layer
│       ├── context/
│       │   └── AuthContext.js
│       └── components/
│           ├── Login.js
│           ├── Dashboard.js
│           ├── SymptomForm.js
│           ├── ReportUpload.js
│           ├── SummaryView.js
│           ├── Recommendations.js
│           └── EmergencyAlert.js
│
├── ml/                         # ML training pipeline
│   ├── models/
│   │   ├── fine_tune_classifier.py    # ClinicalBERT fine-tuning
│   │   └── fine_tune_summarizer.py    # T5/BART fine-tuning
│   ├── rag/
│   │   └── build_faiss_index.py      # FAISS index builder
│   └── preprocessing/
│       └── text_processor.py         # Text cleaning & ICD mapping
│
├── docker/                     # Docker configuration
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
│
├── scripts/
│   ├── setup.sh               # Development setup script
│   └── init_db.sql            # MySQL initialization
│
├── .github/workflows/
│   └── ci.yml                 # GitHub Actions CI/CD
│
└── docker-compose.yml
```

---

## ☁️ Cloud Deployment (AWS)

```
CloudFront (CDN)
      ↓
EC2 (Django + Gunicorn + Nginx)
      ↓
RDS MySQL (Multi-AZ)
      ↓
S3 (Encrypted Report Storage)
      ↓
IAM + KMS (Access Control + Encryption)
```

### AWS Setup
1. Launch EC2 instance (recommended: g4dn.xlarge for GPU, t3.large for CPU-only)
2. Set up RDS MySQL with Multi-AZ
3. Create S3 bucket with server-side encryption (AES-256)
4. Configure IAM roles with least-privilege access
5. Set up CloudFront for frontend CDN

---

## 🧪 Testing

```bash
# Backend tests
cd backend
python manage.py test --verbosity=2

# Run specific test class
python manage.py test tests.SymptomAnalysisTestCase

# Frontend tests
cd frontend
npm test

# Frontend coverage
npm test -- --watchAll=false --coverage
```

### Test Coverage
- User registration/login flows
- Symptom analysis endpoint
- Emergency severity detection (unit + integration)
- Recommendation engine
- RAG system retrieval
- OCR text extraction

---

## 🔒 Security & HIPAA-like Compliance

| Security Measure | Implementation |
|-----------------|---------------|
| Data Encryption (Rest) | AES-256 (AWS KMS / database-level) |
| Data Encryption (Transit) | TLS 1.2+ (HTTPS) |
| Authentication | JWT with refresh token rotation |
| Authorization | Role-based access control (RBAC) |
| Audit Logging | Immutable access logs with timestamps |
| SQL Injection | Django ORM (parameterized queries) |
| XSS Protection | DRF serializer validation + CORS |
| Password Security | PBKDF2 hashing (Django default) |

---

## 📊 Evaluation Metrics

| Task | Metric | Target |
|------|--------|--------|
| Symptom Classification | Accuracy, F1-score | F1 > 0.85 |
| Named Entity Recognition | Precision, Recall | F1 > 0.80 |
| Report Summarization | ROUGE-1/2/L | ROUGE-2 > 0.15 |
| QA/RAG | BLEU | BLEU > 0.20 |

Cross-validation: 5-fold, 80/20 train-test split.

---

## 🔮 Future Enhancements

1. 🎙️ Voice-based symptom input (Whisper ASR)
2. 🌍 Multi-language support (mBERT)
3. ⌚ Wearable device integration (Apple Health, Fitbit)
4. 🔐 Federated learning for privacy-preserving training
5. ❤️ Real-time ECG analysis
6. ⚡ Redis caching for frequent queries
7. 📌 Pinecone vector DB for production scale

---

## ⚕️ Medical Disclaimer

> **MyHealth AI** is an academic prototype for educational purposes only. It is **not** a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider. In an emergency, call **911** immediately.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

*Built for B.Tech Final Year AIML Major Project | Industry-level design rigor*