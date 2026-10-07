from datetime import datetime
from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator


class RecipientInput(BaseModel):
    """
    Accepts recipient inputs at the HTTP envelope layer.
    Permissive so individual validation errors are caught in the worker
    rather than rejecting the entire batch with HTTP 422.
    """
    name: Optional[Any] = None
    email: Optional[Any] = None

    model_config = ConfigDict(extra="allow")


class JobCreateRequest(BaseModel):
    course_name: str = Field(..., min_length=1, description="Course or event name")
    event_date: str = Field(..., min_length=1, description="Date of completion or event")
    issuer: str = Field(..., min_length=1, description="Issuing organization")
    recipients: List[RecipientInput] = Field(..., min_length=1, description="At least one recipient is required")

    @field_validator("course_name", "event_date", "issuer")
    @classmethod
    def validate_non_whitespace(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only")
        return v.strip()


class JobCreateResponse(BaseModel):
    job_id: int
    status: str
    total: int
    message: str


class CertificateItemResponse(BaseModel):
    id: int
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    download_url: Optional[str] = None


class JobDetailResponse(BaseModel):
    job_id: int
    course_name: str
    event_date: str
    issuer: str
    status: str
    total: int
    successful: int
    failed: int
    progress: float
    created_at: datetime
    completed_at: Optional[datetime] = None
    certificates: List[CertificateItemResponse] = []


class CertificateStatusResponse(BaseModel):
    certificate_id: int
    job_id: int
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
    status: str
    error_message: Optional[str] = None
