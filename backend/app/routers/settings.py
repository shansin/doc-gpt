import os
import subprocess

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import _DEFAULT_SYSTEM_PROMPT, settings

router = APIRouter(prefix="/api")


class GpuInfo(BaseModel):
    index: int
    name: str
    vram_total_mb: int
    vram_used_mb: int
    vram_free_mb: int


class GpuSettings(BaseModel):
    ollama_gpu: int
    docling_gpu: int


class GpuSettingsResponse(BaseModel):
    gpus: list[GpuInfo]
    ollama_gpu: int
    docling_gpu: int
    docling_requires_restart: bool


def _get_gpu_info() -> list[GpuInfo]:
    """Query nvidia-smi for GPU info."""
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=index,name,memory.total,memory.used,memory.free",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return []

        gpus = []
        for line in result.stdout.strip().split("\n"):
            parts = [p.strip() for p in line.split(",")]
            if len(parts) == 5:
                gpus.append(GpuInfo(
                    index=int(parts[0]),
                    name=parts[1],
                    vram_total_mb=int(parts[2]),
                    vram_used_mb=int(parts[3]),
                    vram_free_mb=int(parts[4]),
                ))
        return gpus
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


@router.get("/gpu-settings")
async def get_gpu_settings() -> GpuSettingsResponse:
    gpus = _get_gpu_info()
    return GpuSettingsResponse(
        gpus=gpus,
        ollama_gpu=settings.OLLAMA_GPU,
        docling_gpu=settings.DOCLING_GPU,
        docling_requires_restart=False,
    )


@router.put("/gpu-settings")
async def update_gpu_settings(body: GpuSettings) -> GpuSettingsResponse:
    old_docling = settings.DOCLING_GPU
    settings.update_gpu(
        ollama_gpu=body.ollama_gpu,
        docling_gpu=body.docling_gpu,
    )
    # Docling GPU requires restart because CUDA_VISIBLE_DEVICES is process-level
    needs_restart = body.docling_gpu != old_docling
    gpus = _get_gpu_info()
    return GpuSettingsResponse(
        gpus=gpus,
        ollama_gpu=settings.OLLAMA_GPU,
        docling_gpu=settings.DOCLING_GPU,
        docling_requires_restart=needs_restart,
    )


# ── System prompt ──────────────────────────────────────────────────


class SystemPromptResponse(BaseModel):
    system_prompt: str
    is_default: bool


class SystemPromptUpdate(BaseModel):
    system_prompt: str


@router.get("/system-prompt")
async def get_system_prompt() -> SystemPromptResponse:
    return SystemPromptResponse(
        system_prompt=settings.SYSTEM_PROMPT,
        is_default=settings.SYSTEM_PROMPT == _DEFAULT_SYSTEM_PROMPT,
    )


@router.put("/system-prompt")
async def update_system_prompt(body: SystemPromptUpdate) -> SystemPromptResponse:
    prompt = body.system_prompt.strip()
    if prompt:
        settings.update_system_prompt(prompt)
    else:
        settings.reset_system_prompt()
    return SystemPromptResponse(
        system_prompt=settings.SYSTEM_PROMPT,
        is_default=settings.SYSTEM_PROMPT == _DEFAULT_SYSTEM_PROMPT,
    )


@router.delete("/system-prompt")
async def reset_system_prompt() -> SystemPromptResponse:
    settings.reset_system_prompt()
    return SystemPromptResponse(
        system_prompt=settings.SYSTEM_PROMPT,
        is_default=True,
    )
