import uuid
from datetime import datetime, timezone

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    Fusion,
    FusionQuery,
    MatchValue,
    PointStruct,
    Prefetch,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from app.config import settings
from app.models import DocumentInfo
from app.services.sparse_encoder import encode_sparse, encode_sparse_batch


class VectorStore:
    def __init__(self):
        self._client: QdrantClient | None = None
        self._collection = settings.COLLECTION_NAME
        self._collection_ready = False

    @property
    def client(self) -> QdrantClient:
        if self._client is None:
            settings.QDRANT_PATH.mkdir(parents=True, exist_ok=True)
            self._client = QdrantClient(path=str(settings.QDRANT_PATH))
        return self._client

    def _ensure_collection(self, vector_size: int):
        if self._collection_ready:
            return
        collections = [c.name for c in self.client.get_collections().collections]
        if self._collection not in collections:
            self.client.create_collection(
                collection_name=self._collection,
                vectors_config={
                    "dense": VectorParams(
                        size=vector_size, distance=Distance.COSINE
                    ),
                },
                sparse_vectors_config={
                    "sparse": SparseVectorParams(),
                },
            )
        self._collection_ready = True

    def upsert(self, chunks: list[dict], embeddings: list[list[float]]):
        if not chunks:
            return
        self._ensure_collection(len(embeddings[0]))
        now = datetime.now(timezone.utc).isoformat()

        texts = [c["text"] for c in chunks]
        sparse_vectors = encode_sparse_batch(texts)

        points = []
        for chunk, embedding, sparse_vec in zip(chunks, embeddings, sparse_vectors):
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk["text"]))
            points.append(
                PointStruct(
                    id=point_id,
                    vector={
                        "dense": embedding,
                        "sparse": sparse_vec,
                    },
                    payload={
                        "text": chunk["text"],
                        "filename": chunk["filename"],
                        "heading": chunk.get("heading", ""),
                        "ingested_at": now,
                    },
                )
            )
        self.client.upsert(collection_name=self._collection, points=points)

    def search(
        self,
        query_embedding: list[float],
        query_text: str = "",
        top_k: int | None = None,
    ) -> list[dict]:
        """Hybrid search: dense + sparse with Reciprocal Rank Fusion."""
        top_k = top_k or settings.TOP_K
        retrieval_k = settings.RETRIEVAL_TOP_K

        self._ensure_collection(len(query_embedding))

        sparse_query = encode_sparse(query_text) if query_text else None

        # Build prefetch queries for RRF fusion
        prefetches = [
            Prefetch(
                query=query_embedding,
                using="dense",
                limit=retrieval_k,
            ),
        ]

        if sparse_query and any(v != 0.0 for v in sparse_query.values):
            prefetches.append(
                Prefetch(
                    query=sparse_query,
                    using="sparse",
                    limit=retrieval_k,
                ),
            )

        results = self.client.query_points(
            collection_name=self._collection,
            prefetch=prefetches,
            query=FusionQuery(fusion=Fusion.RRF),
            limit=retrieval_k,
            with_payload=True,
        )

        return [
            {
                "text": hit.payload["text"],
                "filename": hit.payload["filename"],
                "score": hit.score,
            }
            for hit in results.points
        ]

    def list_documents(self) -> list[DocumentInfo]:
        docs: dict[str, dict] = {}
        offset = None
        while True:
            result = self.client.scroll(
                collection_name=self._collection,
                limit=100,
                offset=offset,
                with_payload=True,
            )
            points, offset = result
            if not points:
                break
            for point in points:
                fname = point.payload["filename"]
                if fname not in docs:
                    docs[fname] = {
                        "id": fname,
                        "filename": fname,
                        "chunk_count": 0,
                        "ingested_at": point.payload.get("ingested_at", ""),
                    }
                docs[fname]["chunk_count"] += 1
            if offset is None:
                break
        return [DocumentInfo(**d) for d in docs.values()]

    def delete_document(self, doc_id: str):
        self.client.delete(
            collection_name=self._collection,
            points_selector=Filter(
                must=[FieldCondition(key="filename", match=MatchValue(value=doc_id))]
            ),
        )

    def delete_all(self):
        collections = [c.name for c in self.client.get_collections().collections]
        if self._collection in collections:
            self.client.delete_collection(collection_name=self._collection)
            self._collection_ready = False


vector_store = VectorStore()
