from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.models import ChatRequest
from app.services.rag import rag_chat

router = APIRouter(prefix="/api")


@router.post("/chat")
async def chat(request: ChatRequest):
    async def event_stream():
        async for event in rag_chat(
            message=request.message,
            history=request.history,
            chat_model=request.chat_model,
            embed_model=request.embed_model,
        ):
            yield event

    return EventSourceResponse(event_stream())
