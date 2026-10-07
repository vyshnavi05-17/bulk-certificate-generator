from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


def get_current_utc():
    return datetime.now(timezone.utc)


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_name = Column(String(255), nullable=False)
    event_date = Column(String(50), nullable=False)
    issuer = Column(String(255), nullable=False)
    status = Column(String(50), default="processing", nullable=False)  # processing, completed, completed_with_errors, failed
    total_count = Column(Integer, default=0, nullable=False)
    success_count = Column(Integer, default=0, nullable=False)
    failed_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_current_utc, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    certificates = relationship(
        "Certificate",
        back_populates="job",
        cascade="all, delete-orphan",
        order_by="Certificate.id"
    )


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("generation_jobs.id"), nullable=False, index=True)
    recipient_name = Column(String(255), nullable=True)
    recipient_email = Column(String(255), nullable=True)
    status = Column(String(50), default="pending", nullable=False)  # pending, success, failed
    file_path = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_current_utc, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    job = relationship("GenerationJob", back_populates="certificates")
