# PolyChat Data Storage

This folder hosts the persistent database files and initial datasets used to seed and train the chatbot's semantic index.

---

## 📂 File Summary
*   📂 `faqs.json`: The source dataset containing questions, keywords, categories, suggested follow-up questions, and localized translations across English, Hindi, Marathi, Tamil, and Punjabi. This is the source of truth for generating vector index matches.
*   📂 `polychat.db`: The SQLite database containing tables for:
    *   **faq**: Caches resolved question-answer pairs (supports translations).
    *   **session**: Tracks chat session metadata and active language overrides.
    *   **feedback**: Persists thumbs-up / thumbs-down user feedback.

---

## 🗄️ Database Schema & SQLite Migration

The database model is mapped via SQLAlchemy inside `backend/app/models/`. During the Punjabi implementation, we successfully executed a database migration to add `answer_pa` support:

```sql
ALTER TABLE faq ADD COLUMN answer_pa TEXT;
```

When the backend container runs, `init_db()` automatically reads the database configurations and synchronizes the table structures.
