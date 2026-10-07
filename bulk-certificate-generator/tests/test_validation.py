import pytest


def test_validation_missing_course_name(client):
    payload = {
        "event_date": "2026-10-07",
        "issuer": "ABC Learning",
        "recipients": [{"name": "John Doe", "email": "john@example.com"}]
    }
    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 422


def test_validation_empty_course_name_whitespace(client):
    payload = {
        "course_name": "   ",
        "event_date": "2026-10-07",
        "issuer": "ABC Learning",
        "recipients": [{"name": "John Doe", "email": "john@example.com"}]
    }
    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 422


def test_validation_missing_issuer(client):
    payload = {
        "course_name": "Python Fundamentals",
        "event_date": "2026-10-07",
        "recipients": [{"name": "John Doe", "email": "john@example.com"}]
    }
    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 422


def test_validation_missing_recipients_field(client):
    payload = {
        "course_name": "Python Fundamentals",
        "event_date": "2026-10-07",
        "issuer": "ABC Learning"
    }
    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 422


def test_validation_empty_recipients_list(client):
    payload = {
        "course_name": "Python Fundamentals",
        "event_date": "2026-10-07",
        "issuer": "ABC Learning",
        "recipients": []
    }
    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 422
