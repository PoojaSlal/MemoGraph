from hashlib import sha256

from fastapi import APIRouter, File, HTTPException, UploadFile
from sympy import content

from app.repositories.jobs import create_job
from app.repositories.sources import create_source
from app.repositories.users import create_user
from app.schemas.source import UploadSourceResponse
from app.worker.tasks import ingest_source_task

from pathlib import Path

STORAGE_DIR = Path("storage")
STORAGE_DIR.mkdir(exist_ok=True)

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

    storage_path = STORAGE_DIR / filename
    storage_path.write_bytes(content)

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
        metadata={
            "original_filename": filename,
            "storage_path": str(storage_path),
        }
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