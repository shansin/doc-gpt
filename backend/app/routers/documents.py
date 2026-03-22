import atexit
import asyncio
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.config import settings, CONVERTED_DIR
from app.models import IngestRequest
from app.services.chunker import chunk_markdown
from app.services.converter_worker import convert_one as _convert_one, _classify_error
from app.services.docling_service import scan_folder
from app.services.embedder import embed_texts
from app.services.vector_store import vector_store

router = APIRouter(prefix="/api")

_convert_pool = ProcessPoolExecutor(
    max_workers=settings.CONVERT_WORKERS,
)
atexit.register(lambda: _convert_pool.shutdown(wait=False, cancel_futures=True))


def _kill_pool_workers(pool: ProcessPoolExecutor):
    """Terminate stuck worker processes so the pool can spawn fresh ones."""
    import os
    import signal

    for pid in list(pool._processes):
        try:
            os.kill(pid, signal.SIGKILL)
        except (ProcessLookupError, OSError):
            pass


@router.post("/ingest")
async def ingest_documents(request: IngestRequest):
    folder = Path(request.folder_path)
    if not folder.exists() or not folder.is_dir():
        raise HTTPException(status_code=400, detail="Invalid folder path")

    embed_model = request.embed_model or settings.EMBEDDING_MODEL

    async def event_stream():
        files = scan_folder(folder)
        total = len(files)

        if total == 0:
            yield json.dumps({"type": "progress", "filename": "", "step": "done", "current": 0, "total": 0})
            return

        loop = asyncio.get_event_loop()
        timeout = settings.CONVERT_TIMEOUT

        processed = 0
        for file_path in files:
            filename = str(file_path.relative_to(folder))
            processed += 1

            # Convert with timeout — ProcessPoolExecutor lets us
            # actually kill stuck conversions (threads can't be killed).
            try:
                future = loop.run_in_executor(_convert_pool, _convert_one, file_path)
                _, text, error = await asyncio.wait_for(future, timeout=timeout)
            except asyncio.TimeoutError:
                future.cancel()
                # Kill the stuck worker so the pool can spawn a fresh one
                _kill_pool_workers(_convert_pool)
                yield json.dumps({
                    "type": "error", "filename": filename,
                    "message": f"Conversion timed out after {timeout}s",
                    "current": processed, "total": total,
                })
                continue

            if error:
                yield json.dumps({
                    "type": "error", "filename": filename,
                    "message": error, "current": processed, "total": total,
                })
                continue

            try:
                # Save converted markdown to disk, preserving folder structure
                relative = file_path.relative_to(folder)
                md_path = CONVERTED_DIR / relative.with_suffix(".md")
                md_path.parent.mkdir(parents=True, exist_ok=True)
                md_path.write_text(text, encoding="utf-8")

                yield json.dumps({
                    "type": "progress", "filename": filename,
                    "step": "chunking", "current": processed, "total": total,
                })

                chunks = chunk_markdown(
                    text, filename,
                    chunk_size=settings.CHUNK_SIZE,
                    overlap=settings.CHUNK_OVERLAP,
                )

                if chunks:
                    yield json.dumps({
                        "type": "progress", "filename": filename,
                        "step": "embedding", "current": processed, "total": total,
                    })

                    texts = [c["text"] for c in chunks]
                    embeddings = await loop.run_in_executor(
                        None, lambda: embed_texts(texts, model=embed_model)
                    )

                    yield json.dumps({
                        "type": "progress", "filename": filename,
                        "step": "storing", "current": processed, "total": total,
                    })

                    vector_store.upsert(chunks, embeddings)

                yield json.dumps({
                    "type": "progress", "filename": filename,
                    "step": "done", "current": processed, "total": total,
                })

            except Exception as e:
                msg = _classify_error(e)
                yield json.dumps({
                    "type": "error", "filename": filename,
                    "message": msg, "current": processed, "total": total,
                })

    return EventSourceResponse(event_stream())


@router.get("/documents")
async def list_documents():
    try:
        docs = vector_store.list_documents()
        return {"documents": [d.model_dump() for d in docs]}
    except Exception:
        return {"documents": []}


@router.delete("/documents")
async def delete_all_documents():
    try:
        vector_store.delete_all()
        # Remove saved markdown conversions
        import shutil
        if CONVERTED_DIR.exists():
            shutil.rmtree(CONVERTED_DIR)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{doc_id:path}")
async def delete_document(doc_id: str):
    try:
        vector_store.delete_document(doc_id)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
