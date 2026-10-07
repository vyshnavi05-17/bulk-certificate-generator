def test_retrieve_generated_certificate_pdf_success(client):
    """
    Test 6: Retrieving generated certificates.
    Generates a certificate, then calls GET /api/certificates/{id}
    and verifies 200 OK, application/pdf header, and valid binary stream.
    """
    payload = {
        "course_name": "API Design Masterclass",
        "event_date": "2026-10-07",
        "issuer": "Software Craftsmanship Guild",
        "recipients": [
            {"name": "Ada Lovelace", "email": "ada@lovelace.org"}
        ]
    }

    create_res = client.post("/api/jobs", json=payload)
    job_id = create_res.json()["job_id"]

    status_res = client.get(f"/api/jobs/{job_id}")
    cert_id = status_res.json()["certificates"][0]["id"]

    # Retrieve certificate PDF
    pdf_res = client.get(f"/api/certificates/{cert_id}")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert pdf_res.content.startswith(b"%PDF-")
    assert len(pdf_res.content) > 1000


def test_retrieve_nonexistent_certificate_404(client):
    """
    Verifies that requesting a non-existent certificate ID returns 404.
    """
    res = client.get("/api/certificates/999999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_retrieve_failed_certificate_returns_conflict(client):
    """
    Verifies that requesting a certificate that failed generation returns 409 Conflict
    with explicit error details rather than a broken PDF or misleading 404.
    """
    payload = {
        "course_name": "API Design Masterclass",
        "event_date": "2026-10-07",
        "issuer": "Software Craftsmanship Guild",
        "recipients": [
            {"name": "Invalid Recipient", "email": "broken-email-address"}
        ]
    }

    create_res = client.post("/api/jobs", json=payload)
    job_id = create_res.json()["job_id"]

    status_res = client.get(f"/api/jobs/{job_id}")
    cert_id = status_res.json()["certificates"][0]["id"]

    res = client.get(f"/api/certificates/{cert_id}")
    assert res.status_code == 409
    data = res.json()
    assert data["detail"]["status"] == "failed"
    assert "error" in data["detail"]


def test_get_certificate_metadata_info(client):
    """
    Verifies the metadata info endpoint for an individual certificate.
    """
    payload = {
        "course_name": "API Design Masterclass",
        "event_date": "2026-10-07",
        "issuer": "Software Craftsmanship Guild",
        "recipients": [
            {"name": "Linus Torvalds", "email": "linus@kernel.org"}
        ]
    }

    create_res = client.post("/api/jobs", json=payload)
    job_id = create_res.json()["job_id"]

    status_res = client.get(f"/api/jobs/{job_id}")
    cert_id = status_res.json()["certificates"][0]["id"]

    info_res = client.get(f"/api/certificates/{cert_id}/info")
    assert info_res.status_code == 200
    info_data = info_res.json()
    assert info_data["certificate_id"] == cert_id
    assert info_data["recipient_name"] == "Linus Torvalds"
    assert info_data["status"] == "success"
