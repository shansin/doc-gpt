import json
import os
from pathlib import Path


_CONFIG_DIR = Path.home() / ".doc-gpt"
_SETTINGS_FILE = _CONFIG_DIR / "settings.json"
CONVERTED_DIR = _CONFIG_DIR / "converted"


def _load_persisted() -> dict:
    """Load user-persisted settings from disk."""
    try:
        if _SETTINGS_FILE.exists():
            return json.loads(_SETTINGS_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def _save_persisted(data: dict):
    """Write user settings to disk."""
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _SETTINGS_FILE.write_text(json.dumps(data, indent=2))


_DEFAULT_SYSTEM_PROMPT = """\
You are a precise document assistant for personal financial and legal records.

Rules:
- Answer ONLY from the provided context. Never invent or estimate values.
- Quote exact dollar amounts, dates, percentages, and account numbers as they appear.
- Identify document types (W-2, 1099-INT, 1099-SA, 1098, etc.) and reference specific fields or boxes when relevant.
- When multiple years or versions of a document exist, clearly distinguish them by year and source.
- If comparing across documents or years, present the data in a clear table or list.
- If the context does not contain enough information, say what is missing and suggest which document types might have the answer.
- Cite source filenames in your answer."""


class Settings:
    PORT: int = 18420
    QDRANT_PATH: Path = Path.home() / ".doc-gpt" / "qdrant"
    COLLECTION_NAME: str = "documents"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    CHAT_MODEL: str = "llama3.2"
    CHUNK_SIZE: int = 1500
    CHUNK_OVERLAP: int = 200
    TOP_K: int = 8
    RETRIEVAL_TOP_K: int = 30  # candidates fetched before reranking
    SCORE_THRESHOLD: float = 0.2  # minimum RRF score to keep
    RERANK_MODEL: str | None = None  # Ollama model for reranking (None = use CHAT_MODEL)
    CONVERT_WORKERS: int = 1  # serialize conversions to avoid GPU OOM
    CONVERT_TIMEOUT: int = 120  # seconds per file
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    SYSTEM_PROMPT: str = _DEFAULT_SYSTEM_PROMPT

    # GPU assignments (-1 = auto / all GPUs)
    OLLAMA_GPU: int = -1   # main_gpu passed to Ollama requests
    DOCLING_GPU: int = -1  # CUDA_VISIBLE_DEVICES set at startup

    def __init__(self):
        persisted = _load_persisted()
        if "ollama_gpu" in persisted:
            self.OLLAMA_GPU = persisted["ollama_gpu"]
        if "docling_gpu" in persisted:
            self.DOCLING_GPU = persisted["docling_gpu"]
        if "system_prompt" in persisted:
            self.SYSTEM_PROMPT = persisted["system_prompt"]
        # Env var override (set by start_services.sh)
        env_docling = os.environ.get("CUDA_VISIBLE_DEVICES")
        if env_docling is not None and env_docling.isdigit():
            self.DOCLING_GPU = int(env_docling)

    def update_gpu(self, ollama_gpu: int | None = None, docling_gpu: int | None = None):
        persisted = _load_persisted()
        if ollama_gpu is not None:
            self.OLLAMA_GPU = ollama_gpu
            persisted["ollama_gpu"] = ollama_gpu
        if docling_gpu is not None:
            self.DOCLING_GPU = docling_gpu
            persisted["docling_gpu"] = docling_gpu
        _save_persisted(persisted)

    def update_system_prompt(self, prompt: str):
        self.SYSTEM_PROMPT = prompt
        persisted = _load_persisted()
        persisted["system_prompt"] = prompt
        _save_persisted(persisted)

    def reset_system_prompt(self):
        self.SYSTEM_PROMPT = _DEFAULT_SYSTEM_PROMPT
        persisted = _load_persisted()
        persisted.pop("system_prompt", None)
        _save_persisted(persisted)


settings = Settings()
