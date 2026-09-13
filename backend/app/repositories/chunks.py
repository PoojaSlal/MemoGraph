from uuid import UUID

from app.db.postgres import get_connection
from app.ingestion.contracts import DocumentChunk


def create_chunk(chunk: DocumentChunk) -> UUID:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO chunks (
                    id,
                    user_id,
                    source_id,
                    memory_id,
                    chunk_index,
                    content,
                    token_count,
                    embedding_model,
                    embedding_version
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id;
                """,
                (
                    chunk.chunk_id,
                    chunk.user_id,
                    chunk.source_id,
                    chunk.memory_id,
                    chunk.chunk_index,
                    chunk.content,
                    chunk.token_count,
                    chunk.embedding_model,
                    chunk.embedding_version,
                ),
            )

            return cur.fetchone()[0]