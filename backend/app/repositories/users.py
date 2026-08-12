from uuid import UUID

from psycopg.rows import dict_row

from app.db.postgres import get_connection


def create_user(email: str | None = None) -> UUID:
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO users (email)
                VALUES (%s)
                RETURNING id;
                """,
                (email,),
            )

            row = cur.fetchone()

    return row["id"]


def get_user(user_id: UUID) -> dict | None:
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT id, email, created_at, updated_at
                FROM users
                WHERE id = %s;
                """,
                (user_id,),
            )

            return cur.fetchone()
