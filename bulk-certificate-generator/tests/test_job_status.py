import io
import zipfile


def test_job_status_progress_calculation(client):
    """
    Test 4: Verifies job status and progress calculation for a bulk batch.
    """
    payload = {
        "course_name": "Full Stack Web Development",
        "event_date": "2026-10-07",
        "issuer": "Tech Institute",
        "recipients": [
            {"name": "Dev One", "email": "dev1@example.com"},
            {"name": "Dev Two", "email": "dev2@example.com"},
            {"name": "Dev Three", "email": "dev3@example.com"}
        ]
    }

    create_res = client.post("/api/jobs", json=payload)
    assert create_res.status_code == 202
    job_id = create_res.json()["job_id"]

    res = client.get(f"/api/jobs/{job_id}")
    assert res.status_code == 200
    data = res.json()

    assert data["job_id"] == job_id
    assert data["total"] == 3
    assert data["successful"] == 3
    assert data["failed"] == 0
    assert data["progress"] == 100.0
    assert data["status"] == "completed"
    assert len(data["certificates"]) == 3


def test_job_status_not_found(client):
    """
    Verifies that querying a non-existent job returns 404 Not Found.
    """
    res = client.get("/api/jobs/999999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_job_bulk_zip_download(client):
    """
    Verifies that all successful certificates in a job can be downloaded
    together as a ZIP archive.
    """
    payload = {
        "course_name": "Microservices with Python",
        "event_date": "2026-10-07",
        "issuer": "Code Academy",
        "recipients": [
            {"name": "Ken Thompson", "email": "ken@example.com"},
            {"name": "Dennis Ritchie", "email": "dennis@example.com"}
        ]
    }

    create_res = client.post("/api/jobs", json=payload)
    job_id = create_res.json()["job_id"]

    zip_res = client.get(f"/api/jobs/{job_id}/download")
    assert zip_res.status_code == 200
    assert zip_res.headers["content-type"] == "application/zip"

    # Verify zip content
    with zipfile.ZipFile(io.BytesIO(zip_res.content)) as z:
        file_list = z.namelist()
        assert len(file_list) == 2
        for filename in file_list:
            assert filename.endswith(".pdf")
