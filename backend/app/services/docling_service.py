import gc
import logging
import zipfile
from pathlib import Path

from docling.document_converter import DocumentConverter

logger = logging.getLogger(__name__)

_OLE_MAGIC = b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"
_ENC_PACKAGE_UTF16 = b"E\x00n\x00c\x00r\x00y\x00p\x00t\x00e\x00d\x00P\x00a\x00c\x00k\x00a\x00g\x00e\x00"
_ENC_INFO_UTF16 = b"E\x00n\x00c\x00r\x00y\x00p\x00t\x00i\x00o\x00n\x00I\x00n\x00f\x00o\x00"


class PasswordProtectedError(Exception):
    pass


def _check_password_protected(file_path: Path) -> None:
    """Raise PasswordProtectedError if the file is encrypted/password-protected."""
    ext = file_path.suffix.lower()

    if ext == ".pdf":
        with open(file_path, "rb") as f:
            content = f.read()
        if b"/Encrypt" in content:
            raise PasswordProtectedError(
                f"{file_path.name} is password-protected"
            )

    elif ext in (".docx", ".xlsx", ".pptx"):
        # Encrypted OOXML files are repackaged as OLE2 containers,
        # so they are no longer valid ZIP archives.
        if not zipfile.is_zipfile(file_path):
            with open(file_path, "rb") as f:
                magic = f.read(8)
            if magic == _OLE_MAGIC:
                raise PasswordProtectedError(
                    f"{file_path.name} is password-protected"
                )

    elif ext in (".doc", ".xls", ".ppt"):
        with open(file_path, "rb") as f:
            raw = f.read()
        if raw[:8] == _OLE_MAGIC and (
            _ENC_PACKAGE_UTF16 in raw or _ENC_INFO_UTF16 in raw
        ):
            raise PasswordProtectedError(
                f"{file_path.name} is password-protected"
            )


# Extensions handled natively by Docling
_DOCLING_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".pptx", ".xlsx",
    ".png", ".jpg", ".jpeg", ".tiff", ".bmp",
    ".html", ".md",
}

# Plain-text extensions read directly (Docling doesn't support these)
_PLAINTEXT_EXTENSIONS = {".txt", ".rtf", ".csv", ".json", ".xml", ".log"}

SUPPORTED_EXTENSIONS = _DOCLING_EXTENSIONS | _PLAINTEXT_EXTENSIONS

# Module-level converter — each worker process gets its own via fork/spawn
_converter: DocumentConverter | None = None
_convert_count = 0
_GC_EVERY = 10  # run GC every N conversions instead of every file


def _get_converter() -> DocumentConverter:
    global _converter
    if _converter is None:
        _converter = DocumentConverter()
    return _converter


def _maybe_free_gpu_memory():
    """Release cached GPU memory periodically to prevent OOM without thrashing."""
    global _convert_count
    _convert_count += 1
    if _convert_count % _GC_EVERY != 0:
        return
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except (ImportError, RuntimeError):
        pass
    gc.collect()


def convert_file(file_path: Path) -> str:
    ext = file_path.suffix.lower()

    # Read plain-text formats directly instead of sending through Docling
    if ext in _PLAINTEXT_EXTENSIONS:
        text = file_path.read_text(errors="replace")
        return text

    _check_password_protected(file_path)

    try:
        converter = _get_converter()
        result = converter.convert(file_path)
        return result.document.export_to_markdown()
    finally:
        _maybe_free_gpu_memory()


def scan_folder(folder_path: Path) -> list[Path]:
    files: list[Path] = []
    for f in sorted(folder_path.rglob("*")):
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(f)
    return files
