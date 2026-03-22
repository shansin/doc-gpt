"""Lightweight BM25-style sparse encoder for hybrid search.

Produces sparse vectors (indices + values) using hashed token IDs and
BM25-style term-frequency weights with proper length normalization.
This enables keyword matching alongside dense vector similarity in Qdrant.
"""

import math
import re
from collections import Counter

from qdrant_client.models import SparseVector

# Use a large hash space to minimize collisions
_HASH_SPACE = 2**31 - 1

# BM25 parameters
_K1 = 1.2   # term frequency saturation
_B = 0.75   # length normalization strength

# Corpus-level average document length (in tokens). Updated during batch
# encoding; falls back to a reasonable default for single-doc calls.
_DEFAULT_AVG_LEN = 200
_corpus_avg_len: float = _DEFAULT_AVG_LEN

# Simple stopwords to reduce noise
_STOPWORDS = frozenset(
    "a an the is was were be been being have has had do does did will would "
    "shall should may might can could am are is was at by for from in into of "
    "on to with and but or nor not so yet both each few more most other some "
    "such no only own same than too very just because as until while about "
    "between through during before after above below up down out off over "
    "under again further then once here there when where why how all any "
    "every it its he she they them their his her this that these those i me "
    "my we our you your".split()
)

_TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")


def _tokenize(text: str) -> list[str]:
    """Lowercase tokenize, removing stopwords."""
    tokens = _TOKEN_RE.findall(text.lower())
    return [t for t in tokens if t not in _STOPWORDS and len(t) > 1]


def _token_to_index(token: str) -> int:
    """Deterministic hash of a token to a sparse vector index."""
    return hash(token) % _HASH_SPACE


def encode_sparse(text: str, avg_len: float | None = None) -> SparseVector:
    """Encode text into a BM25-style sparse vector.

    Uses BM25 TF saturation: tf_score = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl/avgdl))
    This properly normalises for document length and saturates term frequency.
    """
    tokens = _tokenize(text)
    if not tokens:
        return SparseVector(indices=[0], values=[0.0])

    tf = Counter(tokens)
    doc_len = len(tokens)
    avg_dl = avg_len if avg_len is not None else _corpus_avg_len

    indices = []
    values = []
    for token, count in tf.items():
        idx = _token_to_index(token)
        # BM25 term frequency component
        numerator = count * (_K1 + 1.0)
        denominator = count + _K1 * (1.0 - _B + _B * doc_len / avg_dl)
        weight = numerator / denominator
        indices.append(idx)
        values.append(round(weight, 4))

    return SparseVector(indices=indices, values=values)


def encode_sparse_batch(texts: list[str]) -> list[SparseVector]:
    """Encode a batch of texts into sparse vectors.

    Computes the actual average document length across the batch for
    proper BM25 length normalization.
    """
    global _corpus_avg_len

    if not texts:
        return []

    # Tokenize all texts and compute corpus-level average length
    all_tokens = [_tokenize(t) for t in texts]
    total_tokens = sum(len(toks) for toks in all_tokens)
    avg_len = total_tokens / len(all_tokens) if all_tokens else _DEFAULT_AVG_LEN

    # Update the global average for future single-doc calls (e.g., queries)
    _corpus_avg_len = avg_len

    results = []
    for tokens, text in zip(all_tokens, texts):
        if not tokens:
            results.append(SparseVector(indices=[0], values=[0.0]))
            continue

        tf = Counter(tokens)
        doc_len = len(tokens)

        indices = []
        values = []
        for token, count in tf.items():
            idx = _token_to_index(token)
            numerator = count * (_K1 + 1.0)
            denominator = count + _K1 * (1.0 - _B + _B * doc_len / avg_len)
            weight = numerator / denominator
            indices.append(idx)
            values.append(round(weight, 4))

        results.append(SparseVector(indices=indices, values=values))

    return results
