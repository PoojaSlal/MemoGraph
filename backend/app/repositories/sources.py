from typing import Any
from uuid import UUID

from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app.db.postgres import get_connection


def create_source(
    user_id: UUID,
    filename: str,
    source_type: str,
    file_hash: str,
    file_size_bytes: int,
    metadata: dict[str, Any] | None = None,
) -> UUID:
    """Creates a new active source document for a user."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sources (
                    user_id, filename, source_type, file_hash, file_size_bytes, metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (
                    user_id,
                    filename,
                    source_type,
                    file_hash,
                    file_size_bytes,
                    Jsonb(metadata or {}),
                ),
            )
            source_id: UUID = cur.fetchone()[0]
    return source_id


def get_source_by_id(source_id: UUID, user_id: UUID) -> dict[str, Any] | None:
    """Fetches an active source document by ID for a specific user."""
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT id, user_id, filename, source_type, file_hash, file_size_bytes, metadata, created_at, updated_at
                FROM sources
                WHERE id = %s AND user_id = %s AND deleted_at IS NULL;
                """,
                (source_id, user_id),
            )
            return cur.fetchone()


def soft_delete_source(source_id: UUID, user_id: UUID) -> bool:
    """Sets deleted_at timestamp for a source. Returns True if row was updated."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE sources
                SET deleted_at = NOW()
                WHERE id = %s AND user_id = %s AND deleted_at IS NULL;
                """,
                (source_id, user_id),
            )
            return cur.rowcount > 0
