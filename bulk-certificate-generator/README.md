# Bulk Certificate Generator Backend API

A high-performance, resilient backend service designed to process bulk certificate generation requests for event and course participants. Built with Python 3.12, FastAPI, SQLite, SQLAlchemy, and ReportLab.

---

## Table of Contents
1. [Overview & Core Features](#overview--core-features)
2. [Architecture & Workflow](#architecture--workflow)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Setup & Installation](#setup--installation)
6. [Running the Application](#running-the-application)
7. [API Documentation & Endpoints](#api-documentation--endpoints)
   - [Submit Bulk Job (`POST /api/jobs`)](#1-submit-bulk-generation-job)
   - [Track Job Status & Progress (`GET /api/jobs/{id}`)](#2-track-job-status--progress)
   - [Download Bulk ZIP (`GET /api/jobs/{id}/download`)](#3-download-bulk-zip-archive)
   - [Retrieve Single Certificate PDF (`GET /api/certificates/{id}`)](#4-retrieve-individual-certificate-pdf)
   - [Get Certificate Metadata (`GET /api/certificates/{id}/info`)](#5-get-certificate-metadata)
8. [Two-Level Validation Strategy](#two-level-validation-strategy)
9. [Failure Isolation & Resilience](#failure-isolation--resilience)
10. [Running Automated Tests](#running-automated-tests)
11. [Key Architectural Decisions & Trade-offs](#key-architectural-decisions--trade-offs)
12. [Interview Preparation Guide](#interview-preparation-guide)

---

## Overview & Core Features

* **Bulk Processing:** Accepts requests with multiple recipients in a single call, dispatching PDF rendering asynchronously without blocking the client.
* **Predefined Certificate Template:** Clean, high-resolution landscape certificate generated with ReportLab.
* **Individual Failure Isolation:** Invalid recipient data (such as malformed emails or empty names) marks only that specific certificate record as failed, allowing all remaining valid certificates in the batch to generate uninterrupted.
* **Granular Status & Progress Tracking:** Real-time job progress percentages, total counts, success/failure metrics, and per-recipient status breakdown.
* **Certificate Retrieval:** Directly downloads high-quality PDF files or packages all certificates into a ZIP archive.
* **Comprehensive Automated Tests:** 18 passing tests covering all 6 mandatory assessment criteria.

---

## Architecture & Workflow

```text
 Client
   │
   │ 1. POST /api/jobs
   ▼
┌─────────────────────────────────────────────────────────────┐
│ FastAPI API Layer                                           │
│ ├── Level 1 Validation: Envelope schema (course, date, etc) │
│ ├── Record GenerationJob in Database (status: processing)   │
│ └── Register BackgroundTask worker                          │
└──────────────┬──────────────────────────────────────────────┘
               │
               ├──────────────────────► Returns 202 Accepted {"job_id": 1, ...}
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ Background Worker (Thread-Safe Isolated Session)            │
│ └── For each recipient in job:                              │
│       ├── Level 2 Validation (email format, non-empty name) │
│       ├── If Valid   ──► Render ReportLab PDF ──► SUCCESS   │
│       └── If Invalid ──► Record Error Reason  ──► FAILED    │
│ └── Finalize Job Status: "completed" or                     │
│                          "completed_with_errors"            │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Rationale |
| :--- | :--- | :--- |
| **Language** | Python 3.12 | Modern type hints, high performance. |
| **API Framework** | FastAPI (0.142.2) | Fast execution, built-in background tasks, automatic OpenAPI (`/docs`). |
| **Database** | SQLite + SQLAlchemy (2.1.3) | Zero external server dependencies for frictionless setup; easily swappable with PostgreSQL. |
| **Validation** | Pydantic (2.13.5) | Strict envelope type checking and data normalization. |
| **PDF Engine** | ReportLab (5.0.1) | Standard pure-Python PDF rendering without heavy external C-binaries (like wkhtmltopdf). |
| **Testing** | Pytest (9.1.1) + TestClient | Fast, isolated test suite with temporary file and database fixtures. |
| **Server** | Uvicorn (0.54.0) | High-performance ASGI server. |

---

## Project Structure

```text
bulk-certificate-generator/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application factory & lifespan
│   ├── database.py                 # SQLite engine, SessionLocal, thread safety
│   ├── models.py                   # SQLAlchemy models (GenerationJob, Certificate)
│   ├── schemas.py                  # Pydantic request & response schemas
│   ├── crud.py                     # Database CRUD operations
│   ├── api/
│   │   ├── __init__.py
│   │   ├── jobs.py                 # POST /api/jobs, GET /api/jobs/{id}, ZIP download
│   │   └── certificates.py         # GET /api/certificates/{id} (PDF retrieval)
│   └── services/
│       ├── __init__.py
│       ├── recipient_validator.py  # Level 2 per-recipient validator
│       ├── certificate_generator.py# ReportLab PDF creation & storage manager
│       └── job_processor.py        # Asynchronous background batch processor
├── templates/
│   ├── __init__.py
│   └── certificate_template.py     # Clean ReportLab landscape certificate template
├── generated_certificates/         # Output directory for generated PDF files
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Test fixtures (isolated SQLite DB & temp dirs)
│   ├── test_job_creation.py        # Test 1: Creating a generation job
│   ├── test_validation.py          # Test 2: Input validation
│   ├── test_generation.py          # Test 3: Certificate PDF generation
│   ├── test_job_status.py          # Test 4: Job status & progress tracking
│   ├── test_failure_handling.py    # Test 5: Individual recipient failure isolation
│   └── test_certificate_retrieval.py # Test 6: Certificate retrieval & error handling
├── requirements.txt                # Pinned dependencies
├── .gitignore
├── .env.example
└── README.md
```

---

## Setup & Installation

### 1. Prerequisites
* Python 3.10+ (Python 3.12 recommended)
* `pip` package manager

### 2. Clone / Navigate to project
```bash
cd bulk-certificate-generator
```

### 3. (Optional) Create and activate virtual environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Running the Application

Start the local server with Uvicorn:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running:
* **Interactive API Documentation (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
* **Health Check:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## API Documentation & Endpoints

### 1. Submit Bulk Generation Job
**Endpoint:** `POST /api/jobs`  
**Status:** `202 Accepted`

#### Example Request:
```bash
curl -X POST "http://127.0.0.1:8000/api/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "course_name": "Python Fundamentals",
    "event_date": "2026-10-07",
    "issuer": "ABC Learning Academy",
    "recipients": [
      {
        "name": "John Doe",
        "email": "john.doe@example.com"
      },
      {
        "name": "Jane Smith",
        "email": "invalid-email-address"
      },
      {
        "name": "David Kumar",
        "email": "david.kumar@example.com"
      }
    ]
  }'
```

#### Example Response:
```json
{
  "job_id": 1,
  "status": "processing",
  "total": 3,
  "message": "Bulk generation job accepted and queued for processing."
}
```

---

### 2. Track Job Status & Progress
**Endpoint:** `GET /api/jobs/{job_id}`  
**Status:** `200 OK`

#### Example Request:
```bash
curl -X GET "http://127.0.0.1:8000/api/jobs/1"
```

#### Example Response (After completion):
```json
{
  "job_id": 1,
  "course_name": "Python Fundamentals",
  "event_date": "2026-10-07",
  "issuer": "ABC Learning Academy",
  "status": "completed_with_errors",
  "total": 3,
  "successful": 2,
  "failed": 1,
  "progress": 100.0,
  "created_at": "2026-10-07T15:47:00Z",
  "completed_at": "2026-10-07T15:47:01Z",
  "certificates": [
    {
      "id": 1,
      "recipient_name": "John Doe",
      "recipient_email": "john.doe@example.com",
      "status": "success",
      "error_message": null,
      "download_url": "/api/certificates/1"
    },
    {
      "id": 2,
      "recipient_name": "Jane Smith",
      "recipient_email": "invalid-email-address",
      "status": "failed",
      "error_message": "Invalid email format: The part after the @-sign is not valid.",
      "download_url": null
    },
    {
      "id": 3,
      "recipient_name": "David Kumar",
      "recipient_email": "david.kumar@example.com",
      "status": "success",
      "error_message": null,
      "download_url": "/api/certificates/3"
    }
  ]
}
```

---

### 3. Download Bulk ZIP Archive
**Endpoint:** `GET /api/jobs/{job_id}/download`  
**Status:** `200 OK` (`application/zip`)

Packages all successfully generated certificate PDFs in the job into a single compressed `.zip` archive.

```bash
curl -O -J "http://127.0.0.1:8000/api/jobs/1/download"
```

---

### 4. Retrieve Individual Certificate PDF
**Endpoint:** `GET /api/certificates/{certificate_id}`  
**Status:** `200 OK` (`application/pdf`)

Downloads the generated PDF certificate directly in your browser or client.

```bash
curl -O -J "http://127.0.0.1:8000/api/certificates/1"
```

* If the certificate is still generating: Returns `409 Conflict` with a pending message.
* If the certificate failed validation: Returns `409 Conflict` with the specific failure reason.
* If the certificate does not exist: Returns `404 Not Found`.

---

### 5. Get Certificate Metadata
**Endpoint:** `GET /api/certificates/{certificate_id}/info`  
**Status:** `200 OK`

```json
{
  "certificate_id": 1,
  "job_id": 1,
  "recipient_name": "John Doe",
  "recipient_email": "john.doe@example.com",
  "status": "success",
  "error_message": null
}
```

---

## Two-Level Validation Strategy

A core requirement is: **"A failure while generating one certificate should not unnecessarily prevent other valid certificates in the same job from being generated."**

To solve this, validation is divided into two distinct tiers:

1. **Level 1 — Envelope Validation (Pydantic API Schema):**
   * Validates mandatory top-level attributes (`course_name`, `event_date`, `issuer`).
   * Ensures `recipients` is a non-empty list of items.
   * If any top-level envelope field is missing or empty, the API returns `422 Unprocessable Entity`.
2. **Level 2 — Recipient-Level Validation (Background Worker):**
   * Validates that individual recipient `name` is non-empty.
   * Validates that `email` adheres to standard email formats.
   * If a recipient is invalid, **only that recipient record is updated to `status='failed'`** with a clear explanation stored in `error_message`.
   * Execution immediately continues to process the remaining recipients.

---

## Running Automated Tests

The test suite covers all 6 criteria explicitly required by the evaluation prompt.

To run all tests:
```bash
pytest -v
```

### Breakdown of Test Suites:
1. `tests/test_job_creation.py`: Tests job creation via `POST /api/jobs`, validating 202 Accepted, initial job record, and response payload.
2. `tests/test_validation.py`: Tests request envelope rejection (empty course names, missing issuer, empty recipient lists) returning 422.
3. `tests/test_generation.py`: Verifies that ReportLab creates valid `%PDF-` files on disk with correct layout and file headers.
4. `tests/test_job_status.py`: Verifies `GET /api/jobs/{id}`, checking progress calculations, status transitions, and bulk ZIP exports.
5. `tests/test_failure_handling.py`: Verifies that a batch with mixed valid and invalid records succeeds for valid recipients and isolates invalid ones.
6. `tests/test_certificate_retrieval.py`: Tests `GET /api/certificates/{id}` returning `application/pdf`, handling 404 for missing IDs, and 409 for failed records.

---

## Key Architectural Decisions & Trade-offs

### 1. Asynchronous Background Processing
* **Decision:** Used FastAPI's built-in `BackgroundTasks` instead of synchronous request blocking.
* **Reasoning:** Certificate rendering (PDF generation) is CPU-bound. If a user submits a batch of 100 or 500 recipients, holding the HTTP connection open would cause HTTP client timeouts and degrade server throughput. Returning `202 Accepted` with a `job_id` lets the client poll progress cleanly.

### 2. Isolated Database Sessions for Background Tasks
* **Decision:** Background tasks instantiate a fresh, independent `SessionLocal()` rather than reusing the request-scoped database dependency.
* **Reasoning:** In FastAPI, request-scoped sessions are closed as soon as the HTTP response is sent. Running background tasks on a closed session results in `DetachedInstanceError` or database lock errors.

### 3. ReportLab Canvas vs HTML-to-PDF Converters
* **Decision:** Used native ReportLab canvas primitives.
* **Reasoning:** Pure Python library without external dependencies like headless Chrome or WebKit binaries (e.g. `wkhtmltopdf` or `weasyprint`). This ensures instant cross-platform portability across Windows, Linux, and macOS.

### 4. SQLite as Relational Database
* **Decision:** SQLite with `connect_args={"check_same_thread": False}`.
* **Reasoning:** Requires zero external database server setup while fully supporting relational foreign keys and ACID transactions. The database layer uses SQLAlchemy ORM, meaning migration to PostgreSQL requires simply changing the `DATABASE_URL` environment variable.

---

## Interview Preparation Guide

Anticipated questions and answers for technical review:

* **Q: Why did you choose FastAPI over Django or Flask?**  
  *A:* FastAPI offers native asynchronous background task dispatching, automatic OpenAPI documentation at `/docs`, and clean dependency injection without the heavyweight overhead of Django.

* **Q: How does the system handle an individual failure without failing the entire batch?**  
  *A:* The background loop wraps each recipient in a per-item `try/except` block and performs Level 2 validation. If validation or PDF rendering fails, the exception updates the recipient's record with `status='failed'` and the error reason, then increments `failed_count` and invokes `continue`.

* **Q: How would you scale this application for 50,000 certificates per hour in production?**  
  *A:*
  1. **Message Broker / Task Queue:** Replace FastAPI `BackgroundTasks` with Celery or RQ backed by Redis/RabbitMQ.
  2. **Worker Pool:** Run horizontally scaled containerized workers to process chunks in parallel across multiple CPU cores.
  3. **Database:** Migrate from SQLite to PostgreSQL with connection pooling (e.g. PgBouncer).
  4. **Storage:** Replace local disk storage with AWS S3 or Google Cloud Storage, generating pre-signed download URLs.
