import io
import os
import zipfile
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GenerationJob
from app.schemas import (
    JobCreateRequest,
    JobCreateResponse,
    JobDetailResponse,
    CertificateItemResponse
)
from app.crud import (
    create_generation_job,
    create_initial_certificates,
    get_job_by_id
)
from app.services.job_processor import process_bulk_generation_job

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.post("", response_model=JobCreateResponse, status_code=status.HTTP_202_ACCEPTED)
def create_job(
    payload: JobCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Submits a bulk certificate generation request.
    Validates high-level payload structure, saves initial job state,
    and dispatches asynchronous certificate generation to the background.
    """
    total_recipients = len(payload.recipients)

    job = create_generation_job(
        db=db,
        course_name=payload.course_name,
        event_date=payload.event_date,
        issuer=payload.issuer,
        total_count=total_recipients
    )

    create_initial_certificates(
        db=db,
        job_id=job.id,
        raw_recipients=payload.recipients
    )

    # Dispatch to background task using thread-safe worker
    background_tasks.add_task(process_bulk_generation_job, job.id)

    return JobCreateResponse(
        job_id=job.id,
        status="processing",
        total=total_recipients,
        message="Bulk generation job accepted and queued for processing."
    )


@router.get("/{job_id}", response_model=JobDetailResponse)
def get_job_status(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieves the status and progress of a certificate generation job,
    including individual recipient statuses and retrieval URLs.
    """
    job = get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generation job with ID {job_id} not found."
        )

    processed = job.success_count + job.failed_count
    progress = round((processed / job.total_count) * 100, 2) if job.total_count > 0 else 0.0

    certificate_items = [
        CertificateItemResponse(
            id=cert.id,
            recipient_name=cert.recipient_name,
            recipient_email=cert.recipient_email,
            status=cert.status,
            error_message=cert.error_message,
            download_url=f"/api/certificates/{cert.id}" if cert.status == "success" else None
        )
        for cert in job.certificates
    ]

    return JobDetailResponse(
        job_id=job.id,
        course_name=job.course_name,
        event_date=job.event_date,
        issuer=job.issuer,
        status=job.status,
        total=job.total_count,
        successful=job.success_count,
        failed=job.failed_count,
        progress=progress,
        created_at=job.created_at,
        completed_at=job.completed_at,
        certificates=certificate_items
    )


@router.get("/{job_id}/download")
def download_all_job_certificates(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Optional bonus endpoint: packages all successfully generated certificates
    for a job into a downloadable ZIP archive.
    """
    job = get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generation job with ID {job_id} not found."
        )

    successful_certs = [
        c for c in job.certificates
        if c.status == "success" and c.file_path and os.path.exists(c.file_path)
    ]

    if not successful_certs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No completed certificates are available to download for this job."
        )

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        for cert in successful_certs:
            safe_name = "".join(ch if ch.isalnum() or ch in " _-" else "_" for ch in (cert.recipient_name or f"cert_{cert.id}"))
            zip_filename = f"{safe_name}_{cert.id}.pdf"
            zip_file.write(cert.file_path, arcname=zip_filename)

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="certificates_job_{job_id}.zip"'
        }
    )
