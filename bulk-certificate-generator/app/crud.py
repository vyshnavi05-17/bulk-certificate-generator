from datetime import datetime, timezone
from typing import List, Optional, Any, Dict
from sqlalchemy.orm import Session
from .models import GenerationJob, Certificate


def get_current_utc():
    return datetime.now(timezone.utc)


def create_generation_job(
    db: Session,
    course_name: str,
    event_date: str,
    issuer: str,
    total_count: int
) -> GenerationJob:
    job = GenerationJob(
        course_name=course_name,
        event_date=event_date,
        issuer=issuer,
        status="processing",
        total_count=total_count,
        success_count=0,
        failed_count=0
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def create_initial_certificates(
    db: Session,
    job_id: int,
    raw_recipients: List[Any]
) -> List[Certificate]:
    certificates = []
    for item in raw_recipients:
        # Extract name and email if available
        name = None
        email = None
        if isinstance(item, dict):
            name = str(item.get("name")) if item.get("name") is not None else None
            email = str(item.get("email")) if item.get("email") is not None else None
        elif hasattr(item, "name") or hasattr(item, "email"):
            name = str(item.name) if getattr(item, "name", None) is not None else None
            email = str(item.email) if getattr(item, "email", None) is not None else None

        cert = Certificate(
            job_id=job_id,
            recipient_name=name,
            recipient_email=email,
            status="pending"
        )
        certificates.append(cert)
        db.add(cert)

    db.commit()
    for cert in certificates:
        db.refresh(cert)
    return certificates


def get_job_by_id(db: Session, job_id: int) -> Optional[GenerationJob]:
    return db.query(GenerationJob).filter(GenerationJob.id == job_id).first()


def get_certificate_by_id(db: Session, certificate_id: int) -> Optional[Certificate]:
    return db.query(Certificate).filter(Certificate.id == certificate_id).first()


def update_certificate_result(
    db: Session,
    certificate_id: int,
    status: str,
    file_path: Optional[str] = None,
    error_message: Optional[str] = None
) -> Optional[Certificate]:
    cert = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    if cert:
        cert.status = status
        cert.file_path = file_path
        cert.error_message = error_message
        cert.completed_at = get_current_utc()
        db.commit()
        db.refresh(cert)
    return cert


def finalize_job(
    db: Session,
    job_id: int,
    success_count: int,
    failed_count: int
) -> Optional[GenerationJob]:
    job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
    if job:
        job.success_count = success_count
        job.failed_count = failed_count
        if failed_count == 0:
            job.status = "completed"
        elif success_count == 0:
            job.status = "failed"
        else:
            job.status = "completed_with_errors"
        job.completed_at = get_current_utc()
        db.commit()
        db.refresh(job)
    return job
