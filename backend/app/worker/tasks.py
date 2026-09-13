from uuid import UUID

from app.worker.celery_app import celery_app


@celery_app.task(name="ingest_source")
def ingest_source_task(
    source_id: str,
    user_id: str,
):
    """
    Placeholder ingestion task.

    Later this will:
    - read the source
    - parse
    - chunk
    - embed
    - store vectors
    """

    print(f"Ingesting source {source_id}")

    return {
        "source_id": source_id,
        "user_id": user_id,
        "status": "STARTED",
    }