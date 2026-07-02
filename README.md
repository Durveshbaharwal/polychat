# PolyChat — Multilingual NLP-Based Website QA Chatbot

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-black?logo=vercel)](https://polychat-eight.vercel.app/)
[![Backend API](https://img.shields.io/badge/Backend%20API-Render-46E3B7?logo=render)](https://polychat-backend.onrender.com/api/v1/health)
[![GitHub](https://img.shields.io/badge/Source-GitHub-181717?logo=github)](https://github.com/Durveshbaharwal/polychat)

> **Assignment Submission** — Multilingual NLP-Based Website QA Chatbot  
> Supports **5 languages**: English · Hindi (हिंदी) · Marathi (मराठी) · Tamil (தமிழ்) · Punjabi (ਪੰਜਾਬੀ)

---

## 🌐 Live Deployment

| Component | URL |
|-----------|-----|
| 🖥️ Frontend (React) | https://polychat-eight.vercel.app/ |
| ⚙️ Backend API (FastAPI) | https://polychat-backend.onrender.com |
| 📖 Swagger Docs | https://polychat-backend.onrender.com/docs |

---

## 🗂️ Repository Structure

```
polychat/
├── backend/                   # FastAPI NLP backend
│   ├── app/
│   │   ├── api/v1/            # REST endpoints (chat, session, languages, health)
│   │   ├── core/              # Config, exceptions, security
│   │   ├── database/          # SQLAlchemy async models & sessions
│   │   ├── nlp/               # NLP pipeline: embeddings, FAISS, language detection
│   │   │   ├── embedding_service.py   # sentence-transformers wrapper
│   │   │   ├── faiss_index.py         # FAISS vector index build/search
│   │   │   ├── language_detector.py   # langdetect + Unicode heuristics
│   │   │   ├── conversation_manager.py# Session context & follow-up handling
│   │   │   └── pipeline.py            # Startup orchestration
│   │   ├── services/          # Business logic (chat_service, feedback)
│   │   ├── faqs.json          # Pre-built FAQ dataset (packaged for deployment)
│   │   ├── faiss.index        # Pre-built FAISS vector index (binary)
│   │   └── faiss.meta.json    # FAISS index metadata (FAQ records)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                  # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/        # ChatWidget, ChatInput, LanguageSelector, etc.
│   │   ├── services/api.ts    # Axios API client
│   │   └── types/             # TypeScript type definitions
│   └── package.json
├── data/
│   └── faqs.json              # Master FAQ dataset (24 intents × 5 languages)
├── models/
│   ├── faiss.index            # FAISS semantic index (384-dim, IndexFlatIP)
│   └── faiss.meta.json        # Index metadata store
├── docker-compose.yml         # One-command local stack
└── README.md
```

---

## 🧠 NLP Architecture

### 1. Multilingual Semantic Search (FAISS + Sentence Transformers)

The core NLP engine uses **dense vector embeddings** for intent matching — not keyword matching.

```
User Query
    │
    ▼
[Language Detector] ──── langdetect + Unicode script heuristics
    │
    ▼
[Sentence Transformer] ── paraphrase-multilingual-MiniLM-L12-v2 (384-dim)
    │                      A pre-trained multilingual model supporting 50+ languages
    ▼
[FAISS IndexFlatIP] ───── Cosine similarity search over 24 pre-indexed FAQ vectors
    │
    ▼
[Top-K Results] ──────── Filtered by confidence threshold (0.45)
    │
    ▼
[Multilingual Response] ─ Answer retrieved in user's selected language
```

**Model:** `paraphrase-multilingual-MiniLM-L12-v2`  
**Index:** FAISS `IndexFlatIP` (Inner Product = cosine similarity on L2-normalized vectors)  
**Dimension:** 384  
**FAQs Indexed:** 24 intents across 5 languages

### 2. Language Detection

- **Primary:** `langdetect` library (statistical model)
- **Secondary:** Unicode script range detection (Devanagari → hi/mr, Tamil → ta, Gurmukhi → pa)
- **Smart Override:** If detected language confidence > 0.8, overrides the UI-selected language

### 3. Contextual Conversation Management

The `ConversationManager` maintains per-session context:
- Stores the last 5 turns in memory
- Detects follow-up queries (short sentences ≤ 4 words) and appends them to the previous question
- Enables natural multi-turn conversations like:
  - "Do you offer a free trial?" → "What about for students?"

### 4. REST API (FastAPI)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/session` | Create a new chat session |
| `DELETE` | `/api/v1/session` | Destroy a session |
| `POST` | `/api/v1/chat` | Send a message, get a response |
| `POST` | `/api/v1/feedback` | Submit thumbs up/down feedback |
| `GET` | `/api/v1/languages` | List supported languages |
| `GET` | `/api/v1/health` | Backend health check |

---

## 🚀 Local Setup (Full NLP Stack)

### Prerequisites
- Docker & Docker Compose  
- 4 GB RAM available (for the multilingual sentence-transformer model)

### Step 1 — Clone the repository
```bash
git clone https://github.com/Durveshbaharwal/polychat.git
cd polychat
```

### Step 2 — Configure environment
```bash
cp backend/.env.example backend/.env
```
Edit `backend/.env` if needed (defaults work out of the box).

### Step 3 — Launch the full stack
```bash
docker compose up -d --build
```

> ⚠️ First run downloads the `paraphrase-multilingual-MiniLM-L12-v2` model (~470 MB). Subsequent starts use the cached model from the `models/` volume.

### Step 4 — Access the application
| Service | URL |
|---------|-----|
| 🌐 Web App | http://localhost:3000 |
| 📖 API Docs | http://localhost:8000/docs |
| 🏥 Health | http://localhost:8000/api/v1/health |

### Stop the application
```bash
docker compose down
```

---

## 🛠️ Manual Setup (Without Docker)

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 📦 Dataset & Model Files

| File | Description |
|------|-------------|
| `data/faqs.json` | Master FAQ dataset — 24 intents, answers in 5 languages |
| `models/faiss.index` | Pre-built FAISS binary index (384-dim vectors) |
| `models/faiss.meta.json` | JSON metadata mapping FAISS indices → FAQ records |

The FAISS index is **pre-built** using the sentence-transformer model offline and committed to the repository. This means:
- ✅ The backend loads the index instantly on startup without requiring model inference
- ✅ Semantic similarity search works correctly since both the index and query vectors use the same model
- ✅ Evaluators can inspect the raw vector data in `faiss.meta.json`

---

## 🌍 Supported Languages

| Code | Language | Script |
|------|----------|--------|
| `en` | English | Latin |
| `hi` | Hindi — हिंदी | Devanagari |
| `mr` | Marathi — मराठी | Devanagari |
| `ta` | Tamil — தமிழ் | Tamil |
| `pa` | Punjabi — ਪੰਜਾਬੀ | Gurmukhi |

---

## 📋 Key Dependencies (`requirements.txt`)

| Package | Purpose |
|---------|---------|
| `fastapi` | REST API framework |
| `uvicorn` | ASGI server |
| `sentence-transformers` | Multilingual NLP embeddings |
| `faiss-cpu` | Facebook AI Similarity Search |
| `langdetect` | Language detection |
| `sqlalchemy` + `aiosqlite` | Async SQLite ORM |
| `pydantic-settings` | Environment config |

---

## 🎯 Assignment Checklist

| Requirement | Status |
|-------------|--------|
| Multilingual support (≥4 Indian languages) | ✅ 5 languages (hi, mr, ta, pa, en) |
| Language selection by user | ✅ Dropdown in UI |
| Natural language query understanding | ✅ sentence-transformers + FAISS semantic search |
| Predefined guided FAQs | ✅ 24 intents with suggested questions |
| Follow-up conversation handling | ✅ ConversationManager with session context |
| User feedback collection | ✅ 👍/👎 per response |
| Language detection | ✅ langdetect + Unicode heuristics |
| Intent recognition | ✅ Semantic similarity → intent label |
| Multilingual response generation | ✅ Per-language answer bank |
| REST API integration | ✅ FastAPI with OpenAPI docs |
| Responsive frontend | ✅ React + TypeScript widget |
| Dataset | ✅ `data/faqs.json` (24 × 5 languages) |
| Trained model files | ✅ `models/faiss.index` + `faiss.meta.json` |
| README with setup instructions | ✅ This document |
| requirements.txt | ✅ `backend/requirements.txt` |
| GitHub deployment | ✅ https://github.com/Durveshbaharwal/polychat |
