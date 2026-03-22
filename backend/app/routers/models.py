import ollama
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api")


@router.get("/models")
async def list_models():
    try:
        response = ollama.list()
        models = [
            {"name": m.model, "size": m.size}
            for m in response.models
        ]
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to list Ollama models: {e}")
