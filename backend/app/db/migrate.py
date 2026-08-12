import logging
from pathlib import Path

from app.db.postgres import get_connection

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def ensure_migrations_table(conn) -> None:
    """Creates the migration tracking table if it does not exist."""
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(255) PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        )


def get_applied_migrations(conn) -> set[str]:
    """Returns migrations that have already been applied."""
    with conn.cursor() as cur:
        cur.execute("SELECT version FROM schema_migrations;")
        return {row[0] for row in cur.fetchall()}


def run_migrations() -> None:
    """Executes all unapplied SQL migrations in order."""
    with get_connection() as conn:
        ensure_migrations_table(conn)
        applied = get_applied_migrations(conn)

        sql_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

        if not sql_files:
            logger.info("No migration files found.")
            return

        for sql_file in sql_files:
            version = sql_file.name

            if version in applied:
                logger.info(
                    "Migration [%s] already applied. Skipping.",
                    version,
                )
                continue

            logger.info("Applying migration [%s]...", version)

            sql_content = sql_file.read_text(encoding="utf-8")

            with conn.cursor() as cur:
                cur.execute(sql_content)
                cur.execute(
                    """
                    INSERT INTO schema_migrations (version)
                    VALUES (%s);
                    """,
                    (version,),
                )

            logger.info(
                "Successfully applied migration [%s]",
                version,
            )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_migrations()
