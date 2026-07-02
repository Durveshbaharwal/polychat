# PolyChat Backend Engine

This is the FastAPI-powered backend server for PolyChat. It hosts the NLP vector search engine, session management, language routers, and SQLite database connectors.

---

## 🏗️ Directory Tour
```
backend/
├── app/
│   ├── api/             # API Router definitions (endpoints for chat, feedback, languages)
│   ├── core/            # App configurations, logging, and exception handlers
│   ├── database/        # Database session and initialization helpers
│   ├── middleware/      # CORSMiddleware and request ID tracing middleware
│   ├── models/          # SQLAlchemy Database Models (FAQ, Feedback, Session)
│   ├── nlp/             # NLP Core: FAISS vector index, embedding model preloader
│   ├── schemas/         # Pydantic schemas validation
│   ├── services/        # Chat service orchestration and feedback recorders
│   └── main.py          # FastAPI application entry point
├── tests/               # PyTest suite for NLP & API testing
├── Dockerfile           # Multi-stage python build configuration
└── requirements.txt     # Python dependency locks
```

---

## ⚙️ Core Components

### 1. NLP Pipeline (`app/nlp/`)
*   **Embedding Service (`embedding.py`)**: Uses the HuggingFace `SentenceTransformer` model to generate 384-dimensional dense vectors. It preloads the model on startup so that the first API request receives a sub-500ms response.
*   **FAISS Vector Index (`faiss_index.py`)**: Implements `faiss.IndexFlatIP` (Inner Product / Cosine Similarity) to match incoming user questions to FAQ intents. The index is built from `data/faqs.json` and saved to `models/faiss.index` to bypass rebuild steps on container restart.
*   **Language Detector (`language_detector.py`)**: Integrates `langdetect` with a deterministic seed to classify input queries. Supports English, Hindi, Marathi, Tamil, and Punjabi.

### 2. Services (`app/services/`)
*   **Chat Service (`chat_service.py`)**: Coordinates incoming requests. It determines the effective language, loads conversation history, invokes FAISS semantic matching, and updates session state.
*   **Conversation Manager (`conversation_manager.py`)**: Implements session history context. If a user enters a short query (<= 3 words) or trigger words (like "what about", "how"), the manager links it as a follow-up to the preceding question.

---

## 🔌 API Summary
*   `POST /api/v1/chat`: Processes user messages, matches intent, and returns translations.
*   `POST /api/v1/feedback`: Records thumbs-up / thumbs-down ratings for responses.
*   `GET /api/v1/languages`: Returns the list of 5 supported languages and metadata.
*   `GET /api/v1/health`: Checks dependencies and resource statuses.
