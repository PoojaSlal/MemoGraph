from typing import Any
from uuid import UUID
from psycopg.rows import dict_row

from app.db.postgres import get_connection


def create_memory(
    user_id: UUID, source_id: UUID, summary: str, memory_type: str
) -> UUID:
    """Creates a logical extracted memory unit linked to a source."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO memories (user_id, source_id, summary, memory_type)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                (user_id, source_id, summary, memory_type),
            )
            memory_id: UUID = cur.fetchone()[0]
    return memory_id


def get_memories_by_source(source_id: UUID, user_id: UUID) -> list[dict[str, Any]]:
    """Fetches all active memories extracted from a specific source."""
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT id, user_id, source_id, summary, memory_type, created_at, updated_at
                FROM memories
                WHERE source_id = %s AND user_id = %s AND deleted_at IS NULL
                ORDER BY created_at ASC;
                """,
                (source_id, user_id),
            )
            return cur.fetchall()
