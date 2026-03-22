from pydantic import BaseModel


class IngestRequest(BaseModel):
    folder_path: str
    embed_model: str | None = None


class ChatRequest(BaseModel):
    message: str
    chat_model: str | None = None
    embed_model: str | None = None
    history: list[dict] | None = None


class DocumentInfo(BaseModel):
    id: str
    filename: str
    chunk_count: int
    ingested_at: str


class ChatSource(BaseModel):
    filename: str
    chunk_text: str
    score: float
