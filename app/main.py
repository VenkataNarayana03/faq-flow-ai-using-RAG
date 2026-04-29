import os
from contextlib import asynccontextmanager
from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# ---------------------------------------------------------------------------
# Point sentence-transformers cache to a stable sub-directory so the model
# is always stored in the same place across runs.
# ---------------------------------------------------------------------------
os.environ.setdefault(
    "SENTENCE_TRANSFORMERS_HOME",
    str(ROOT_DIR / ".cache" / "sentence_transformers"),
)

from app.routes.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-warm the embedding model at startup to avoid cold-start delays."""
    print("[startup] Loading embedding model…")
    from app.services.retriever import get_embedding_model
    get_embedding_model()   # downloads + caches on first run
    print("[startup] Embedding model ready.")
    yield                   # server is now live


app = FastAPI(title="FAQFlow AI", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://faq-flow-ai-using-rag.onrender.com",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")
app.mount("/ui", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get("/")
def home():
    return {
        "message": "FAQFlow AI running",
        "chat_endpoint": "/api/chat",
        "frontend": "/ui",
    }


if __name__ == "__main__":
    import asyncio
    import uvicorn
    import socket
    import sys

    # WinError 10054 is harmless Windows-only asyncio noise (client disconnect).
    # Switching to SelectorEventLoop suppresses it in local dev logs.
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    def find_free_port(start_port=8000):
        port = start_port
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('127.0.0.1', port))
                    return port
                except OSError:
                    print(f"Port {port} is in use, trying {port + 1}...")
                    port += 1

    port = find_free_port(8000)
    print(f"Starting server on http://127.0.0.1:{port}")
    print(f"Frontend available at http://127.0.0.1:{port}/ui")
    uvicorn.run("app.main:app", host="127.0.0.1", port=port)
