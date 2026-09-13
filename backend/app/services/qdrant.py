from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.core.config import settings

COLLECTION_NAME = "memograph_chunks"

qdrant_client = QdrantClient(
    host=settings.qdrant_host,
    port=settings.qdrant_port,
)


def ensure_collection():
    collections = qdrant_client.get_collections().collections
    names = [c.name for c in collections]

    if COLLECTION_NAME not in names:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=384,                 # MiniLM dimension
                distance=Distance.COSINE,
            ),
        )

#all-MiniLM-L6-v2 produces 384-dimensional vectors.