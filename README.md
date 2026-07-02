# PolyChat: Multilingual NLP QA Chatbot (Interview Assignment)

Welcome to **PolyChat**, an embeddable, production-ready multilingual virtual assistant. This repository showcases a full-stack engineering solution that leverages Semantic Search and Natural Language Processing (NLP) to resolve user FAQs in 5 languages: **English, Hindi (हिंदी), Marathi (मराठी), Tamil (தமிழ்), and Punjabi (ਪੰਜਾਬੀ)**.

Designed as an interview assignment submission, the architecture focuses on containerization, high performance, robust language detection, and context retention for conversational follow-ups.

---

## 🗺️ Project Guided Tour

This monorepo is split into distinct functional domains. Here is an overview of the directories:

```
LingLing/
├── backend/          # FastAPI server (NLP engine, DB logic, API routers)
├── frontend/         # React + TypeScript + Tailwind CSS widget & landing page
├── data/             # Persistent SQLite database & FAQ JSON datasets
├── models/           # Persisted FAISS vector index & HuggingFace cache
└── docker-compose.yml
```

### Directory Handbooks
For detailed explanations, setup steps, and configuration parameters of each component, check their individual sub-READMEs:
*   📂 **[Backend Engine](file:///c:/ASUS/Projects/LingLing/backend/README.md)**: FastAPI architectures, Pydantic schemas, language detection heuristics, and NLP pipeline.
*   📂 **[Frontend Widget](file:///c:/ASUS/Projects/LingLing/frontend/README.md)**: React components, Tailwind styling, Zustand state store, and custom markdown bold formatting parser.
*   📂 **[Data Store](file:///c:/ASUS/Projects/LingLing/data/README.md)**: FAQ schema definition and SQLite migrations.
*   📂 **[Vector Models](file:///c:/ASUS/Projects/LingLing/models/README.md)**: Semantic embedding model details and FAISS index persistence.

---

## 🚀 Quick Start Guide

### Prerequisites
*   Docker & Docker Compose installed.
*   Minimum **4GB RAM** allocated to Docker (required for downloading and preloading the multilingual semantic model).

### Spinning Up the Project
From the root directory, run:
```bash
docker compose up -d --build
```
> ⚠️ **Note:** The first execution will take a few minutes as it downloads the `paraphrase-multilingual-MiniLM-L12-v2` transformer model (approx. 470MB) and preloads it into container memory for sub-500ms responses.

### Local Endpoints
*   🌐 **Web App (Landing Page & Widget):** [http://localhost:3000](http://localhost:3000)
*   🔌 **FastAPI API Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
*   🏥 **Backend Health Endpoint:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 🛠️ Tech Stack & Key Architectures

### 1. NLP Semantic Search Engine
Instead of basic keyword matching, PolyChat computes 384-dimensional dense vector embeddings of user queries using Sentence Transformers. These are indexed using **FAISS (Facebook AI Similarity Search)**. This allows the bot to match synonyms, colloquial phrasing, and typos to the correct intent with high confidence.

### 2. Robust Multilingual Routing
1.  **Language Detection**: Queries are analyzed deterministically via `langdetect`.
2.  **Smart Override**: If a user selects a language in the widget dropdown but types in another language (e.g. asking in Hindi while on the Tamil UI), the system's confidence threshold routes it to the detected query language.
3.  **Graceful Fallback**: If a query is not translated, the system reverts to English while providing a localized language fallback prompt.

### 3. Contextual Conversation Manager
To support follow-up questions (e.g., "Do you offer a free trial?" followed by "What about Saturday?"), the backend maintains session history. It uses a short-sentence heuristic to concatenate follow-up context with the previous question, enabling natural conversational flow.

---

## 🛑 Stopping the Application
To stop all containers and release network ports, execute:
```bash
docker compose down
```
