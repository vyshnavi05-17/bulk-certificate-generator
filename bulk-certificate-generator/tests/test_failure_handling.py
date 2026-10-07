import os


def test_individual_certificate_failure_isolation(client):
    """
    Test 5: Handling an individual certificate failure.
    Demonstrates that invalid recipients do NOT kill the entire job:
    valid recipients generate successfully while invalid ones are marked failed with descriptive reasons.
    """
    payload = {
        "course_name": "Resilient Systems Engineering",
        "event_date": "2026-10-07",
        "issuer": "Engineering Institute",
        "recipients": [
            {"name": "Valid Recipient One", "email": "valid1@example.com"},
            {"name": "Invalid Email Person", "email": "not-an-email"},
            {"name": "", "email": "emptyname@example.com"},
            {"name": "Valid Recipient Two", "email": "valid2@example.com"}
        ]
    }

    create_res = client.post("/api/jobs", json=payload)
    assert create_res.status_code == 202
    job_id = create_res.json()["job_id"]

    status_res = client.get(f"/api/jobs/{job_id}")
    assert status_res.status_code == 200
    data = status_res.json()

    assert data["total"] == 4
    assert data["successful"] == 2
    assert data["failed"] == 2
    assert data["status"] == "completed_with_errors"
    assert data["progress"] == 100.0

    certs = {c["id"]: c for c in data["certificates"]}

    # First recipient: success
    cert_1 = data["certificates"][0]
    assert cert_1["recipient_name"] == "Valid Recipient One"
    assert cert_1["status"] == "success"
    assert cert_1["error_message"] is None
    assert cert_1["download_url"] is not None

    # Second recipient: failed due to bad email
    cert_2 = data["certificates"][1]
    assert cert_2["status"] == "failed"
    assert cert_2["error_message"] is not None
    assert "email" in cert_2["error_message"].lower()

    # Third recipient: failed due to empty name
    cert_3 = data["certificates"][2]
    assert cert_3["status"] == "failed"
    assert cert_3["error_message"] is not None
    assert "name" in cert_3["error_message"].lower()

    # Fourth recipient: success despite preceding failures
    cert_4 = data["certificates"][3]
    assert cert_4["recipient_name"] == "Valid Recipient Two"
    assert cert_4["status"] == "success"
    assert cert_4["error_message"] is None
    assert cert_4["download_url"] is not None


def test_job_with_all_failed_recipients(client):
    """
    Verifies that if every recipient in a batch is invalid, the job completes
    with status='failed' rather than crashing.
    """
    payload = {
        "course_name": "Resilient Systems Engineering",
        "event_date": "2026-10-07",
        "issuer": "Engineering Institute",
        "recipients": [
            {"name": "", "email": "bad1"},
            {"name": "   ", "email": "bad2"}
        ]
    }

    create_res = client.post("/api/jobs", json=payload)
    assert create_res.status_code == 202
    job_id = create_res.json()["job_id"]

    status_res = client.get(f"/api/jobs/{job_id}")
    assert status_res.status_code == 200
    data = status_res.json()

    assert data["total"] == 2
    assert data["successful"] == 0
    assert data["failed"] == 2
    assert data["status"] == "failed"
