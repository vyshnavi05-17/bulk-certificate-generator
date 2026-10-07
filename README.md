# Bulk Certificate Generator Backend API

A Python-based backend API for generating certificates in bulk from a predefined certificate template.

The system allows a client to submit a single request containing certificate information and multiple recipients. A generation job is created and processed in the background, while each recipient is validated and processed independently. Valid recipients receive generated PDF certificates, while invalid recipients are marked as failed with an appropriate error message without interrupting the remaining valid records.

## Key Features

* **Bulk Certificate Generation** — Process multiple recipients through a single API request.
* **Background Job Processing** — Uses FastAPI BackgroundTasks to process certificate generation without keeping the client request open.
* **Recipient-Level Validation** — Validates recipient names and email addresses independently.
* **Failure Isolation** — A failed recipient does not prevent other valid recipients from receiving certificates.
* **Predefined PDF Template** — Generates certificates using a single ReportLab-based template.
* **Job Progress Tracking** — Tracks total, successful, failed, and overall processing progress.
* **Certificate Retrieval** — Download individual generated certificates through a dedicated API endpoint.
* **Bulk ZIP Download** — Download all successfully generated certificates for a job as a ZIP archive.
* **Relational Database** — Uses SQLite with SQLAlchemy for job and certificate tracking.
* **Automated Testing** — Includes 18 tests covering job creation, validation, generation, status tracking, failure handling, and certificate retrieval.

## Technology Stack

* Python 3.12
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic
* ReportLab
* Pytest
* Uvicorn

## Processing Flow

```text
Client
  │
  │ POST /api/jobs
  ▼
Create Generation Job
  │
  ▼
Background Processing
  │
  ├── Validate Recipient
  │      ├── Invalid → FAILED + error
  │      └── Valid
  │             ↓
  │        Generate PDF
  │             ↓
  │          SUCCESS
  │
  ▼
Update Job Progress
  │
  ▼
GET /api/jobs/{job_id}
  │
  ├── View progress and results
  └── Retrieve generated certificates
```

## Assessment Focus

This project was designed to demonstrate backend development fundamentals including REST API design, request validation, relational data modeling, background processing, error isolation, file generation, status tracking, and automated testing.
