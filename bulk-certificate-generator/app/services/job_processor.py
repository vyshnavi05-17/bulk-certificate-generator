import logging
from typing import Optional
from app.database import get_isolated_db
from app.crud import (
    get_job_by_id,
    update_certificate_result,
    finalize_job
)
from app.services.recipient_validator import validate_recipient_data
from app.services.certificate_generator import generate_certificate_file

logger = logging.getLogger(__name__)


def process_bulk_generation_job(job_id: int, storage_dir: Optional[str] = None):
    """
    Background worker function that processes all recipients for a job.
    Uses its own isolated database session to avoid connection lifecycle issues.
    """
    db = get_isolated_db()
    try:
        job = get_job_by_id(db, job_id)
        if not job:
            logger.error(f"Job {job_id} not found in background processor.")
            return

        success_count = 0
        failed_count = 0

        # Iterate through each certificate record
        for cert in job.certificates:
            try:
                # Level 2 validation: validate individual recipient data
                is_valid, validation_err, cleaned_data = validate_recipient_data({
                    "name": cert.recipient_name,
                    "email": cert.recipient_email
                })

                if not is_valid:
                    # Record recipient-level validation failure
                    update_certificate_result(
                        db=db,
                        certificate_id=cert.id,
                        status="failed",
                        file_path=None,
                        error_message=validation_err
                    )
                    failed_count += 1
                    continue

                # Recipient is valid -> update cleaned name/email if normalized
                cert.recipient_name = cleaned_data["name"]
                cert.recipient_email = cleaned_data["email"]

                # Generate certificate PDF
                file_path = generate_certificate_file(
                    job_id=job.id,
                    certificate_id=cert.id,
                    recipient_name=cleaned_data["name"],
                    course_name=job.course_name,
                    event_date=job.event_date,
                    issuer=job.issuer,
                    storage_dir=storage_dir
                )

                # Record success
                update_certificate_result(
                    db=db,
                    certificate_id=cert.id,
                    status="success",
                    file_path=file_path,
                    error_message=None
                )
                success_count += 1

            except Exception as exc:
                # Catch generation or unexpected per-record error
                logger.exception(f"Error processing certificate {cert.id} for job {job_id}: {exc}")
                update_certificate_result(
                    db=db,
                    certificate_id=cert.id,
                    status="failed",
                    file_path=None,
                    error_message=f"Generation error: {str(exc)}"
                )
                failed_count += 1
                continue

        # Finalize job status
        finalize_job(
            db=db,
            job_id=job.id,
            success_count=success_count,
            failed_count=failed_count
        )

    except Exception as exc:
        logger.exception(f"Fatal error while processing job {job_id}: {exc}")
    finally:
        db.close()
