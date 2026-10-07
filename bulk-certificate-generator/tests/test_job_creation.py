def test_create_generation_job_success(client):
    """
    Test 1: Creating a generation job.
    Submits a bulk job request and verifies 202 status, job_id, status, and total count.
    """
    payload = {
        "course_name": "Python Fundamentals",
        "event_date": "2026-10-07",
        "issuer": "ABC Learning Academy",
        "recipients": [
            {"name": "Alice Johnson", "email": "alice@example.com"},
            {"name": "Bob Smith", "email": "bob@example.com"},
            {"name": "Charlie Davis", "email": "charlie@example.com"}
        ]
    }

    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 202

    data = response.json()
    assert "job_id" in data
    assert data["job_id"] is not None
    assert data["status"] == "processing"
    assert data["total"] == 3
    assert "message" in data


def test_create_generation_job_single_recipient(client):
    """
    Verifies that a job with a single recipient is also accepted properly.
    """
    payload = {
        "course_name": "Cloud Computing",
        "event_date": "2026-11-15",
        "issuer": "Cloud Org",
        "recipients": [
            {"name": "David Miller", "email": "david@example.com"}
        ]
    }

    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert data["total"] == 1
