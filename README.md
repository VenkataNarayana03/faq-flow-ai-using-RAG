# 🤖 FAQFlow AI — RAG-Powered Customer Support Chatbot

**FAQFlow AI** is a production-deployed, AI-powered chatbot that answers customer support questions using **Retrieval-Augmented Generation (RAG)**. Instead of relying purely on an LLM's training data, it retrieves the most relevant FAQ entries from a vector database and uses them as grounded context before generating an answer.

> 🌐 **Live Demo:** Local App
> 🔌 **Backend API:** `http://localhost:8000`

---

## 📌 What Problem Does It Solve?

Generic LLMs (like GPT or Llama) answer from training data and can hallucinate. This project solves that by:

1. **Storing real FAQ data** as vectors in Pinecone
2. **Retrieving the most relevant FAQs** for every question (semantic search)
3. **Passing them as context** to the LLM so answers are grounded in real data

---

## 🧠 How RAG Works (Big Picture)

```
User types a question
        │
        ▼
 ┌─────────────────┐
 │  Frontend UI    │  (HTML/CSS/JavaScript)
 │  script.js      │  Sends POST /api/chat
 └────────┬────────┘
          │ HTTP Request
          ▼
 ┌─────────────────┐
 │  FastAPI Server │  (app/main.py)
 │  /api/chat      │  Receives query
 └────────┬────────┘
          │
          ▼
 ┌─────────────────────────────────────────┐
 │           RAG Pipeline                  │
 │  (app/services/rag.py)                  │
 │                                         │
 │  1. Get chat history (memory.py)        │
 │  2. Retrieve context (retriever.py)     │
 │  3. Generate answer (generator.py)      │
 │  4. Update memory (memory.py)           │
 └──────┬─────────────────────┬────────────┘
        │                     │
        ▼                     ▼
 ┌────────────┐      ┌──────────────────┐
 │  Pinecone  │      │  Groq / OpenAI   │
 │  Vector DB │      │  LLM API         │
 │            │      │  (llama-3.1-8b)  │
 │ Semantic   │      │                  │
 │ Search     │      │  Generates final │
 │ → Top FAQs │      │  answer          │
 └────────────┘      └──────────────────┘
        │
        ▼
 ┌──────────────────────────┐
 │  HuggingFace Inference   │
 │  API                     │
 │  (all-MiniLM-L6-v2)     │
 │  Converts text → vector  │
 └──────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | HTML, CSS, JavaScript | Chat UI in the browser |
| **Backend** | Python + FastAPI | REST API server |
| **Embeddings** | HuggingFace Inference API (`all-MiniLM-L6-v2`) | Converts text to 384-dimensional vectors |
| **Vector DB** | Pinecone | Stores and searches FAQ embeddings |
| **LLM (default)** | Groq (`llama-3.1-8b-instant`) | Generates final answers |
| **LLM (optional)** | OpenAI (`gpt-4o-mini`) | Alternative LLM provider |
| **Data Source** | HuggingFace Datasets (`MakTek/Customer_support_faqs_dataset`) | Raw FAQ training data |

| **Config** | python-dotenv | Secure environment variable management |

---

## 📁 Full Project Structure

```
faqflow-ai/
│
├── app/                          ← Backend (FastAPI)
│   ├── main.py                   ← App entry point, CORS, routes, static files
│   ├── config/
│   │   └── settings.py           ← Loads .env variables, validates API keys
│   ├── models/
│   │   └── schema.py             ← Pydantic request/response models
│   ├── routes/
│   │   └── chat.py               ← POST /api/chat endpoint
│   └── services/
│       ├── rag.py                ← Orchestrates the full RAG pipeline
│       ├── retriever.py          ← Embeds query + searches Pinecone
│       ├── generator.py          ← Calls Groq/OpenAI LLM to generate answer
│       └── memory.py             ← Stores in-memory chat history
│
├── data/
│   ├── raw/
│   │   └── faqs.jsonl            ← Raw FAQ records downloaded from HuggingFace
│   └── processed/
│       └── faqs.jsonl            ← Cleaned records ready for embedding
│
├── scripts/                      ← One-time data pipeline scripts
│   ├── load_data.py              ← Downloads FAQ dataset → data/raw/
│   ├── preprocess.py             ← Cleans raw data → data/processed/
│   └── embed_store.py            ← Embeds + uploads vectors to Pinecone
│
├── frontend/                     ← Browser UI (served at /ui)
│   ├── index.html                ← Chat page structure
│   ├── style.css                 ← Glassmorphism-style UI design
│   └── script.js                 ← Chat logic, API calls, message rendering
│
├── .env                          ← API keys (NOT committed to git)
├── .gitignore                    ← Excludes .env, __pycache__, etc.
├── requirements.txt              ← Python dependencies
├── architecture.drawio           ← Visual architecture diagram
└── README.md                     ← This file
```

---

## 🔍 File-by-File Explanation

### Backend

---

#### `app/main.py` — FastAPI Application Entry Point

The root of the backend server.

**What it does:**
- Creates the FastAPI app instance
- Adds **CORS middleware** — allows the local frontend to call the backend without browser security errors
- Registers the `/api/chat` route via `chat_router`
- Serves the frontend HTML/CSS/JS files at `/ui`
- Exposes a health check endpoint at `/`
- Includes smart **auto port detection** locally — if port 8000 is busy, it tries 8001, 8002, etc.

```python
# Key lines:
app.include_router(chat_router, prefix="/api")          # Chat API
app.mount("/ui", StaticFiles(directory="frontend"))      # Frontend UI
```

---

#### `app/config/settings.py` — Configuration & Environment Variables

Loads all secrets and settings from the `.env` file.

**Variables it manages:**

| Variable | Purpose |
|---|---|
| `PINECONE_API_KEY` | Authenticate with Pinecone |
| `PINECONE_INDEX` | Name of your Pinecone index |
| `PINECONE_NAMESPACE` | Optional namespace inside the index |
| `EMBEDDING_MODEL` | HuggingFace model name (default: `all-MiniLM-L6-v2`) |
| `HF_API_KEY` | HuggingFace token for Inference API |
| `LLM_PROVIDER` | `groq` (default) or `openai` |
| `GROQ_API_KEY` | Groq API key |
| `GROQ_MODEL` | Groq model name (default: `llama-3.1-8b-instant`) |
| `OPENAI_API_KEY` | OpenAI API key (optional) |
| `OPENAI_MODEL` | OpenAI model name (default: `gpt-4o-mini`) |

Also includes `require_setting()` — raises a clear error if a required key is missing instead of failing silently.

---

#### `app/models/schema.py` — Request & Response Models

Pydantic data models for the API.

- `ChatRequest` — expects `{ "query": "..." }` from the frontend
- `ChatResponse` — returns `{ "answer": "...", "contexts": [...] }` to the frontend

These ensure type safety and automatic API documentation.

---

#### `app/routes/chat.py` — Chat API Endpoint

Defines the single API endpoint:

```
POST /api/chat
```

**What it does:**
1. Receives the user query from the frontend
2. Passes it to `rag_pipeline()`
3. Returns the LLM answer and retrieved contexts back to the frontend

This is the only bridge between the frontend and the AI logic.

---

#### `app/services/rag.py` — RAG Pipeline Orchestrator

The central coordinator that runs the full Retrieval-Augmented Generation flow.

**Step-by-step:**
1. Cleans/strips the user query
2. Calls `retrieve(query)` → gets top 5 matching FAQ texts from Pinecone
3. Calls `get_history()` → fetches last 10 conversation turns
4. Calls `generate_answer(query, contexts, history)` → LLM generates grounded answer
5. Calls `update_history(query, answer)` → saves the turn to memory
6. Returns `{ "answer": ..., "contexts": [...] }`

---

#### `app/services/retriever.py` — Semantic Search

Handles converting text into vectors and searching Pinecone.

**What it does:**
1. Calls the **HuggingFace Inference API** with the user query
2. Gets back a 384-dimensional float vector (the "meaning" of the query)
3. Sends that vector to Pinecone
4. Pinecone finds the top-5 most similar stored FAQ vectors
5. Extracts and returns the FAQ text from metadata (deduplicating results)



---

#### `app/services/generator.py` — LLM Answer Generation

Builds the prompt and calls the LLM to generate a final answer.

**Prompt structure:**
```
[System]: You are a helpful customer support assistant. Answer using
          retrieved context. Suggest 1-2 follow-up questions.

[User]:   Chat History: {last 10 messages}
          Retrieved Context: {top FAQ matches}
          Question: {user query}
```

**Supports two LLM providers:**

| Provider | Model | How to activate |
|---|---|---|
| **Groq** (default) | `llama-3.1-8b-instant` | Default — no change needed |
| **OpenAI** | `gpt-4o-mini` | Set `LLM_PROVIDER=openai` in `.env` |

Temperature is set to `0.2` — low randomness for factual customer support answers.

---

#### `app/services/memory.py` — Conversation History

Simple in-memory chat history store.

```python
chat_history = []  # Grows as the conversation progresses
```

- `get_history()` — returns the last 10 messages as a string for the prompt
- `update_history(query, answer)` — appends each user/bot turn

> **Note:** Memory resets when the server restarts (not persisted to disk or DB). This is a known limitation of the free-tier deployment.

---

### Data Pipeline Scripts

These are **one-time setup scripts** — run them locally before deployment to populate Pinecone.

---

#### `scripts/load_data.py` — Download FAQ Dataset

Downloads customer support FAQs from HuggingFace and saves to `data/raw/faqs.jsonl`.

**Sources:**
- **Primary:** `MakTek/Customer_support_faqs_dataset` (200 Q&A pairs)
- **Optional:** `squad` dataset (general QA — disabled by default)
- **Fallback:** 3 built-in starter FAQs if HuggingFace is unavailable

**Run:**
```powershell
$env:USE_HF_DATASETS="true"
python scripts/load_data.py
```

---

#### `scripts/preprocess.py` — Clean Raw Data

Reads `data/raw/faqs.jsonl` and produces clean records in `data/processed/faqs.jsonl`.

**What it cleans:**
- Strips extra whitespace from all fields
- Skips records missing a question or answer
- Combines question + answer + context into a single `text` field used for embedding
- Assigns a unique `id` to each record (`faq-0`, `faq-1`, ...)

**Run:**
```powershell
python scripts/preprocess.py
```

---

#### `scripts/embed_store.py` — Embed & Upload to Pinecone

Reads processed records, generates embeddings using `sentence-transformers` locally (used only during setup), and uploads vectors to Pinecone in batches of 100.

**Each Pinecone vector stores:**
```json
{
  "id": "faq-42",
  "values": [0.023, -0.118, ...],   ← 384 float numbers
  "metadata": {
    "question": "How can I track my order?",
    "answer": "You can track your order by...",
    "text": "Question: How can I track... Answer: ...",
    "source": "MakTek/Customer_support_faqs_dataset"
  }
}
```

**Run:**
```powershell
python scripts/embed_store.py
```

---

### Frontend

---

#### `frontend/index.html` — Chat Page

The main HTML page users see. Contains:
- Page `<title>` and meta tags (SEO)
- Chat message display area (`#messages`)
- Text input field (`#message-input`)
- Send button
- Clear chat button (`#clear-chat`)
- Link to `style.css` and `script.js`

---

#### `frontend/style.css` — Glassmorphism UI Styling

A modern, sleek UI with:
- Dark-mode glassmorphism design (frosted glass card on gradient background)
- Google Fonts (`Inter`) for clean typography
- Smooth fade-in animations for each message
- User messages right-aligned (blue), bot messages left-aligned (white)
- Responsive layout for different screen sizes
- Hover effects on buttons

---

#### `frontend/script.js` — Chat Logic & API Communication

Handles all browser-side behavior:

1. **Backend URL detection:**
   - Local dev (`localhost`) → `http://127.0.0.1:8000/api/chat`

2. **Sending messages:**
   - Captures user input on form submit
   - Shows "Thinking..." placeholder while waiting
   - POSTs `{ "query": "..." }` to `/api/chat`

3. **Rendering responses:**
   - Detects bullet-point lists in the response and renders them as `<ul>`
   - Falls back to paragraph formatting otherwise

4. **Error handling:**
   - Shows a friendly message if the backend is unreachable

5. **Clear chat** button resets the conversation view

---

## 🔑 Environment Variables (`.env`)

```env
# Pinecone
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX=faq-rag
PINECONE_NAMESPACE=                      # Optional, leave blank if not using namespaces

# HuggingFace (for embeddings API - avoids loading model locally)
HF_API_KEY=hf_your_token_here
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# LLM (Groq is default and free)
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant

# Optional: OpenAI
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini
```

> ⚠️ **Never commit `.env` to GitHub.** It is listed in `.gitignore`.

---

## 🚀 Local Setup Guide

### 1. Clone and Install

```powershell
git clone https://github.com/VenkataNarayana03/faq-flow-ai-using-RAG.git
cd faq-flow-ai-using-RAG
python -m pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root with all required keys (see above).

### 3. Run the Data Pipeline (First Time Only)

```powershell
# Download FAQ dataset
$env:USE_HF_DATASETS="true"
python scripts/load_data.py

# Clean data
python scripts/preprocess.py

# Upload to Pinecone
python scripts/embed_store.py
```

Expected result: **200 FAQ vectors** in Pinecone.

### 4. Start the Backend

```powershell
python -m uvicorn app.main:app --reload
```

### 5. Open the App

| URL | Purpose |
|---|---|
| `http://127.0.0.1:8000/ui/` | Chat UI |
| `http://127.0.0.1:8000/` | Health check |
| `http://127.0.0.1:8000/docs` | Swagger API docs |

---

## 📡 API Reference

### `POST /api/chat`

**Request:**
```json
{
  "query": "How can I track my order?"
}
```

**Response:**
```json
{
  "answer": "You can track your order by logging into your account and navigating to Order History. You'll find a tracking link next to each order.\n\nYou might also want to ask:\n- What do I do if my tracking link isn't working?\n- How long does delivery usually take?",
  "contexts": [
    "Question: How can I track my order? Answer: You can track your order from the order history page using the tracking link."
  ]
}
```

---



## 🔧 Useful Debug Commands

```powershell
# Check how many vectors are in Pinecone
python -c "from pinecone import Pinecone; from app.config.settings import PINECONE_API_KEY,PINECONE_INDEX; pc=Pinecone(api_key=PINECONE_API_KEY); index=pc.Index(PINECONE_INDEX); print(index.describe_index_stats())"

# Test retrieval directly
python -c "from app.services.retriever import retrieve; print(retrieve('How can I track my order?', top_k=3))"

# Test the full API locally
python -c "from fastapi.testclient import TestClient; from app.main import app; c=TestClient(app); r=c.post('/api/chat', json={'query':'How can I track my order?'}); print(r.json())"
```

---

## ⚠️ Known Limitations

| Limitation | Reason | Fix |
|---|---|---|
| Chat memory resets on restart | Stored in RAM, not a database | Add Redis or a DB for persistent sessions |
| Slow first message after idle | Render free tier sleeps | Upgrade to paid tier or add a keep-alive ping |
| No user authentication | Out of scope for this demo | Add OAuth or JWT tokens |
| Single shared memory | All users share the same history | Add session-based memory per user |

---

## 📊 Current Verified State

- ✅ `data/raw/faqs.jsonl` — 200 customer FAQ records
- ✅ `data/processed/faqs.jsonl` — 200 cleaned records
- ✅ Pinecone index — 200 vectors, dimension 384, metric cosine
- ✅ `/api/chat` — working
- ✅ `/ui/` — working
- ✅ LLM: Groq `llama-3.1-8b-instant`
- ✅ Embeddings: HuggingFace Inference API `all-MiniLM-L6-v2`

---

## 👨‍💻 Author

**Venkata Narayana**
GitHub: [@VenkataNarayana03](https://github.com/VenkataNarayana03)
