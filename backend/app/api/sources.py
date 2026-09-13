from hashlib import sha256

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.repositories.jobs import create_job
from app.repositories.sources import create_source
from app.repositories.users import create_user
from app.schemas.source import UploadSourceResponse
from app.worker.tasks import ingest_source_task

router = APIRouter(prefix="/sources", tags=["Sources"])

SUPPORTED_TYPES = {".txt": "TXT", ".md": "MD"}


@router.post("/upload")
async def upload_source(
    file: UploadFile = File(...),
):
    filename = file.filename or ""

    extension = "." + filename.split(".")[-1].lower()

    if extension not in SUPPORTED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only TXT and MD files are supported.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    user_id = create_user()

    source_id = create_source(
        user_id=user_id,
        filename=filename,
        source_type=SUPPORTED_TYPES[extension],
        file_hash=sha256(content).hexdigest(),
        file_size_bytes=len(content),
        metadata={"original_filename": filename},
    )

    job_id = create_job(
        user_id=user_id,
        source_id=source_id,
    )

    ingest_source_task.delay(
        str(source_id),
        str(user_id),
    )

    return UploadSourceResponse(
        source_id=source_id,
        job_id=job_id,
        status="QUEUED",
        filename=filename,
    )