import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud import get_certificate_by_id
from app.schemas import CertificateStatusResponse

router = APIRouter(prefix="/api/certificates", tags=["Certificates"])


@router.get("/{certificate_id}")
def retrieve_certificate_pdf(
    certificate_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieves and downloads the generated PDF for an individual certificate.
    Returns:
        - 200 OK (application/pdf) if successfully generated.
        - 404 Not Found if certificate ID does not exist.
        - 409 Conflict if certificate is still processing or failed.
    """
    cert = get_certificate_by_id(db, certificate_id)
    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certificate with ID {certificate_id} was not found."
        )

    if cert.status == "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "status": "pending",
                "message": "Certificate is currently being generated. Please check again shortly."
            }
        )

    if cert.status == "failed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "status": "failed",
                "error": cert.error_message or "Certificate generation failed."
            }
        )

    if not cert.file_path or not os.path.exists(cert.file_path):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Certificate file is missing from server storage."
        )

    safe_recipient_name = "".join(
        c if c.isalnum() or c in " _-" else "_" for c in (cert.recipient_name or f"recipient_{cert.id}")
    )
    download_filename = f"certificate_{safe_recipient_name}_{cert.id}.pdf"

    return FileResponse(
        path=cert.file_path,
        media_type="application/pdf",
        filename=download_filename
    )


@router.get("/{certificate_id}/info", response_model=CertificateStatusResponse)
def get_certificate_metadata(
    certificate_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieves metadata and generation status for a specific certificate ID.
    """
    cert = get_certificate_by_id(db, certificate_id)
    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certificate with ID {certificate_id} was not found."
        )

    return CertificateStatusResponse(
        certificate_id=cert.id,
        job_id=cert.job_id,
        recipient_name=cert.recipient_name,
        recipient_email=cert.recipient_email,
        status=cert.status,
        error_message=cert.error_message
    )
