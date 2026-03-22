"""Standalone conversion function for ProcessPoolExecutor workers.

Kept in its own module so spawned worker processes only import
docling_service — not vector_store, embedder, or other services
that hold resources (DB locks, GPU handles) in the parent process.
"""

from pathlib import Path

from app.services.docling_service import PasswordProtectedError, convert_file


def _classify_error(e: Exception) -> str:
    if isinstance(e, PasswordProtectedError):
        return str(e)

    msg = str(e)

    if "is not valid" in msg:
        return "File is corrupted or unreadable"
    if "CUDA out of memory" in msg:
        return "Not enough GPU memory to process this file"
    if "Pipeline" in msg and "failed" in msg:
        return "Document conversion pipeline crashed (file may be too large or complex)"

    if not msg or msg == "None":
        return type(e).__name__
    if len(msg) > 200:
        return msg[:200] + "..."
    return msg


def convert_one(file_path: Path) -> tuple[Path, str | None, str | None]:
    """Convert a single file, returning (path, markdown, error)."""
    try:
        text = convert_file(file_path)
        if not text or not text.strip():
            return (file_path, None, "Conversion produced no text")
        return (file_path, text, None)
    except Exception as e:
        return (file_path, None, _classify_error(e))
