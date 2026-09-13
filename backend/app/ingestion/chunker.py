from app.ingestion.contracts import DocumentChunk, ParsedDocument


DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50


def chunk_document(
    document: ParsedDocument,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[DocumentChunk]:
    """
    Splits a ParsedDocument into overlapping retrieval chunks.

    Args:
        document: Normalized document produced by a parser.
        chunk_size: Maximum number of characters per chunk.
        overlap: Number of characters shared between consecutive chunks.

    Returns:
        A list of DocumentChunk objects.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0:
        raise ValueError("overlap cannot be negative.")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size.")

    content = document.content

    chunks: list[DocumentChunk] = []

    start = 0
    chunk_index = 0

    while start < len(content):
        end = min(start + chunk_size, len(content))
        chunk_content = content[start:end]

        chunks.append(
            DocumentChunk(
                source_id=document.source_id,
                user_id=document.user_id,
                content=chunk_content,
                chunk_index=chunk_index,
                token_count=len(chunk_content.split()),
            )
        )

        chunk_index += 1

        if end >= len(content):
            break

        start = end - overlap

    return chunks