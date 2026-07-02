# PolyChat NLP Models & Vectors

This folder stores the local semantic search indexes and the cached HuggingFace neural model files.

---

## 📂 File Summary
*   📂 `faiss.index`: The Facebook AI Similarity Search index. It stores the pre-computed high-dimensional mathematical vector mappings for the FAQs.
*   📂 `faiss.meta.json`: Flat metadata store matching FAISS indices back to categories, answers, and suggested questions.
*   📂 `huggingface/`: Cache directory containing the locally downloaded `paraphrase-multilingual-MiniLM-L12-v2` transformer model weights.

---

## 🔬 NLP Processing Mechanics

1.  **Vectorizer Pipeline**: We use `sentence-transformers` to map question strings to a 384-dimension real-valued space.
2.  **FAISS Engine**: FAISS computes the cosine similarity between the vector representation of the user's input and the stored FAQ vectors.
3.  **Performance Optimization**: By keeping `faiss.index` cached in this volume directory, startup initialization checks if the files exist. If they do, the server loads them instantly, bypassing vectorization indexing costs (saving substantial CPU usage on boot). If `data/faqs.json` changes, deleting these files forces the backend pipeline to rebuild the indexes on the next startup.
