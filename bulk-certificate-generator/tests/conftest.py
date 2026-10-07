import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
import app.database as db_module
import app.services.certificate_generator as cert_gen_module
from app.main import app


@pytest.fixture(scope="session")
def test_engine(tmp_path_factory):
    """Creates a temporary SQLite database engine for testing."""
    db_file = tmp_path_factory.mktemp("db") / "test_certificates.db"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(autouse=True)
def setup_test_environment(test_engine, tmp_path, monkeypatch):
    """
    Ensures each test gets clean database tables and an isolated certificate storage directory.
    """
    # Create fresh tables
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    # Configure session maker for test engine
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Monkeypatch the database module session makers
    monkeypatch.setattr(db_module, "engine", test_engine)
    monkeypatch.setattr(db_module, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(db_module, "get_isolated_db", lambda: TestingSessionLocal())

    # Configure isolated certificate storage directory
    certs_dir = tmp_path / "test_generated_certs"
    certs_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(cert_gen_module, "DEFAULT_STORAGE_DIR", str(certs_dir))

    # Override get_db dependency in FastAPI app
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()


@pytest.fixture
def client():
    """Returns a FastAPI TestClient."""
    with TestClient(app) as test_client:
        yield test_client
