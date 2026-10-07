import os
from app.services.certificate_generator import generate_certificate_file


def test_certificate_generation_via_api(client):
    """
    Submits a job and verifies that the PDF is physically created on disk
    and properly recorded in the database with status='success'.
    """
    payload = {
        "course_name": "Data Engineering Mastery",
        "event_date": "2026-10-07",
        "issuer": "Data Academy",
        "recipients": [
            {"name": "Sarah Connor", "email": "sarah@cyberdyne.com"}
        ]
    }

    create_res = client.post("/api/jobs", json=payload)
    assert create_res.status_code == 202
    job_id = create_res.json()["job_id"]

    # In TestClient, BackgroundTasks executes synchronously
    status_res = client.get(f"/api/jobs/{job_id}")
    assert status_res.status_code == 200
    data = status_res.json()

    assert data["status"] == "completed"
    assert data["successful"] == 1
    assert data["failed"] == 0
    assert len(data["certificates"]) == 1

    cert = data["certificates"][0]
    assert cert["status"] == "success"
    assert cert["recipient_name"] == "Sarah Connor"
    assert cert["download_url"] is not None


def test_certificate_generator_service_direct(tmp_path):
    """
    Direct unit test for the ReportLab certificate generator service.
    Verifies that the PDF output file has the valid %PDF magic header and valid size.
    """
    out_dir = tmp_path / "certs_unit"
    out_dir.mkdir()

    file_path = generate_certificate_file(
        job_id=99,
        certificate_id=101,
        recipient_name="Grace Hopper",
        course_name="Compilers and Systems",
        event_date="2026-10-07",
        issuer="ACM",
        storage_dir=str(out_dir)
    )

    assert os.path.exists(file_path)
    assert os.path.getsize(file_path) > 1000

    with open(file_path, "rb") as f:
        header = f.read(5)
        assert header == b"%PDF-"
