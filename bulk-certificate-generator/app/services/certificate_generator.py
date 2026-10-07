import os
from typing import Optional
from templates.certificate_template import draw_certificate_pdf

DEFAULT_STORAGE_DIR = os.getenv("CERTIFICATE_STORAGE_DIR", "./generated_certificates")


class CertificateGenerationError(Exception):
    """Raised when PDF rendering or file generation fails."""
    pass


def generate_certificate_file(
    job_id: int,
    certificate_id: int,
    recipient_name: str,
    course_name: str,
    event_date: str,
    issuer: str,
    storage_dir: Optional[str] = None
) -> str:
    """
    Generates and saves the certificate PDF to disk.
    Returns the absolute or relative file path to the generated PDF.
    """
    target_dir = storage_dir or DEFAULT_STORAGE_DIR
    os.makedirs(target_dir, exist_ok=True)

    filename = f"certificate_job{job_id}_{certificate_id}.pdf"
    file_path = os.path.join(target_dir, filename)

    try:
        draw_certificate_pdf(
            output_path=file_path,
            recipient_name=recipient_name,
            course_name=course_name,
            event_date=event_date,
            issuer=issuer,
            certificate_id=certificate_id
        )
        return file_path
    except Exception as exc:
        raise CertificateGenerationError(f"Failed to generate certificate PDF: {str(exc)}") from exc
