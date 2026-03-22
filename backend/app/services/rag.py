import json
from collections.abc import AsyncGenerator

import ollama

from app.config import settings
from app.services.embedder import embed_texts
from app.services.vector_store import vector_store


def _hyde_expand(
    query: str,
    model: str,
    gpu_opts: dict | None,
) -> str | None:
    """Generate a hypothetical document snippet that would answer the query.

    This is embedded alongside the original query to improve retrieval
    against factual/tabular documents (HyDE technique).
    """
    prompt = (
        "Given the following question about personal documents, "
        "write a short passage (2-3 sentences) that would appear in a document "
        "answering this question. Include realistic placeholder values. "
        "Do NOT answer the question — just write what the source document would say.\n\n"
        f"Question: {query}"
    )

    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options=gpu_opts,
        )
        return response.message.content.strip()
    except ollama.ResponseError:
        return None


def _build_query_embedding(
    query: str,
    hyde_text: str | None,
    embed_model: str,
) -> list[float]:
    """Embed the query, optionally averaging with HyDE embedding."""
    if hyde_text:
        embeddings = embed_texts([query, hyde_text], model=embed_model)
        # Average the two embeddings
        return [
            (a + b) / 2.0 for a, b in zip(embeddings[0], embeddings[1])
        ]
    return embed_texts([query], model=embed_model)[0]


_CONTEXT_SUFFIX = "\n\nContext:\n{context}"


async def rag_chat(
    message: str,
    history: list[dict] | None = None,
    chat_model: str | None = None,
    embed_model: str | None = None,
) -> AsyncGenerator[str, None]:
    chat_model = chat_model or settings.CHAT_MODEL
    embed_model = embed_model or settings.EMBEDDING_MODEL

    gpu_opts: dict | None = None
    if settings.OLLAMA_GPU >= 0:
        gpu_opts = {"main_gpu": settings.OLLAMA_GPU}

    # 1. HyDE — generate a hypothetical answer for better retrieval
    hyde_text = _hyde_expand(message, model=chat_model, gpu_opts=gpu_opts)

    # 2. Build query embedding (averaged with HyDE if available)
    query_embedding = _build_query_embedding(message, hyde_text, embed_model)

    # 3. Hybrid search (dense + sparse with RRF)
    results = vector_store.search(query_embedding, query_text=message)

    # 4. Score threshold filtering — drop low-relevance results
    results = [r for r in results if r["score"] >= settings.SCORE_THRESHOLD]

    # 5. Take top-K (RRF fusion already ranked them well)
    results = results[: settings.TOP_K]

    context_parts = []
    sources = []
    for r in results:
        context_parts.append(f"[{r['filename']}]\n{r['text']}")
        sources.append({
            "filename": r["filename"],
            "chunk_text": r["text"][:200],
            "score": r["score"],
        })

    context = "\n\n---\n\n".join(context_parts)

    system_prompt = settings.SYSTEM_PROMPT + _CONTEXT_SUFFIX.format(context=context)

    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": message})

    stream = ollama.chat(
        model=chat_model, messages=messages, stream=True, options=gpu_opts
    )
    for chunk in stream:
        content = chunk.message.content
        if content:
            yield json.dumps({"type": "delta", "content": content})

    yield json.dumps({"type": "sources", "sources": sources})
