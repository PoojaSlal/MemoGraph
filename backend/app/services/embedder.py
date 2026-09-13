from sentence_transformers import SentenceTransformer
from app.ingestion.contracts import DocumentChunk

MODEL_NAME = "all-MiniLM-L6-v2"

# Load ONCE when the service starts
_model = SentenceTransformer(MODEL_NAME)


def get_model() -> SentenceTransformer:
    return _model


def embed_chunks(chunks: list[DocumentChunk]) -> list[DocumentChunk]:
    if not chunks:
        return []

    texts = [chunk.content for chunk in chunks]
    embeddings = _model.encode(texts, normalize_embeddings=True)

    for chunk, vector in zip(chunks, embeddings):
        chunk.embedding = vector.tolist()

    return chunks