from typing import Any
from uuid import UUID
from psycopg.rows import dict_row

from app.db.postgres import get_connection


def create_job(user_id: UUID, source_id: UUID, status: str = "QUEUED") -> UUID:
    """Creates a background ingestion job linked to an existing source."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO jobs (user_id, source_id, status)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (user_id, source_id, status),
            )
            job_id: UUID = cur.fetchone()[0]
    return job_id


def update_job_status(
    job_id: UUID,
    user_id: UUID,
    status: str,
    error_message: str | None = None,
) -> bool:
    """Updates status and error details for a specific user's job."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE jobs
                SET status = %s,
                    error_message = %s
                WHERE id = %s
                  AND user_id = %s;
                """,
                (status, error_message, job_id, user_id),
            )
            return cur.rowcount > 0


def get_job_by_id(job_id: UUID, user_id: UUID) -> dict[str, Any] | None:
    """Fetches job details for a specific user."""
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT id, user_id, source_id, status, error_message, retry_count, created_at, updated_at
                FROM jobs
                WHERE id = %s AND user_id = %s;
                """,
                (job_id, user_id),
            )
            return cur.fetchone()
