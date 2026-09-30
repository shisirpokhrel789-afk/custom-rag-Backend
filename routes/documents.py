from pathlib import Path
from tempfile import NamedTemporaryFile
import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from database.connection import get_db
from services.ingestion import IngestionService


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

ALLOWED_EXTENSIONS = {".pdf", ".txt"}


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:

    filename = file.filename or "unknown"
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    temporary_file_path = None

    try:
        with NamedTemporaryFile(
            suffix=extension,
            delete=False,
        ) as temporary_file:

            temporary_file.write(content)
            temporary_file_path = temporary_file.name

        service = IngestionService(db)

        chunk_count = service.ingest(
            file_path=temporary_file_path,
            filename=filename,
            file_type=extension,
        )

        return {
            "filename": filename,
            "chunks_created": chunk_count,
            "message": "Document successfully ingested.",
        }

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Document ingestion failed: {exc}",
        ) from exc

    finally:
        if temporary_file_path and os.path.exists(temporary_file_path):
            os.remove(temporary_file_path)
