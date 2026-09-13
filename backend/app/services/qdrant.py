from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import settings
from app.ingestion.contracts import DocumentChunk


COLLECTION_NAME = "memograph_chunks"
VECTOR_SIZE = 384


qdrant_client = QdrantClient(
    host=settings.qdrant_host,
    port=settings.qdrant_port,
)


def ensure_collection():
    collections = qdrant_client.get_collections().collections
    names = [collection.name for collection in collections]

    if COLLECTION_NAME not in names:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )


def upsert_chunks(chunks: list[DocumentChunk]) -> None:
    points = []

    for chunk in chunks:
        if chunk.embedding is None:
            raise ValueError(
                f"Chunk {chunk.chunk_id} does not have an embedding."
            )

        points.append(
            PointStruct(
                id=str(chunk.chunk_id),
                vector=chunk.embedding,
                payload={
                    "user_id": str(chunk.user_id),
                    "source_id": str(chunk.source_id),
                    "chunk_id": str(chunk.chunk_id),
                    "chunk_index": chunk.chunk_index,
                    "memory_id": (
                        str(chunk.memory_id)
                        if chunk.memory_id
                        else None
                    ),
                    "content": chunk.content,
                    "embedding_model": chunk.embedding_model,
                    "embedding_version": chunk.embedding_version,
                },
            )
        )

    if points:
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )