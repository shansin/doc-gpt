import ollama

from app.config import settings


def _gpu_options() -> dict | None:
    """Return Ollama options dict with GPU assignment if configured."""
    if settings.OLLAMA_GPU >= 0:
        return {"main_gpu": settings.OLLAMA_GPU}
    return None


def embed_texts(texts: list[str], model: str | None = None) -> list[list[float]]:
    model = model or settings.EMBEDDING_MODEL
    opts = _gpu_options()
    response = ollama.embed(model=model, input=texts, options=opts)
    return response.embeddings


def embed_query(text: str, model: str | None = None) -> list[float]:
    return embed_texts([text], model=model)[0]
