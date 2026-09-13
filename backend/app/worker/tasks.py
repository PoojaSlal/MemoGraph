from pathlib import Path
from uuid import UUID

from app.ingestion.text_parser import parse_text_file
from app.ingestion.chunker import chunk_document
from app.repositories.chunks import create_chunk
from app.repositories.jobs import update_job_by_source
from app.repositories.memories import create_memory
from app.repositories.sources import get_source_by_id
from app.services.embedder import embed_chunks
from app.worker.celery_app import celery_app

from app.services.qdrant import upsert_chunks

@celery_app.task(name="ingest_source")
def ingest_source_task(source_id: str, user_id: str):
    source = get_source_by_id(UUID(source_id), UUID(user_id))

    update_job_by_source(UUID(source_id), UUID(user_id), "PROCESSING")

    document = parse_text_file(
        Path(source["metadata"]["storage_path"]),
        UUID(source_id),
        UUID(user_id),
    )

    memory_id = create_memory(
        UUID(user_id),
        UUID(source_id),
        summary=document.content[:200],
        memory_type="FACT",
    )

    chunks = chunk_document(document)

    for chunk in chunks:
        chunk.memory_id = memory_id

    embed_chunks(chunks)

    for chunk in chunks:
        create_chunk(chunk)

    upsert_chunks(chunks)

    update_job_by_source(
        UUID(source_id),
        UUID(user_id),
        "COMPLETED",
    )
    return {
        "chunks": len(chunks),
        "status": "COMPLETED",
    }