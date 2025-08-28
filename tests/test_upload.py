import pytest

try:
    from fastapi.testclient import TestClient
    from fastapi import HTTPException
    from main import app
    from api import upload
except ModuleNotFoundError:  # pragma: no cover
    pytest.skip("fastapi not installed", allow_module_level=True)

from .utils import (
    create_text_bytes,
    create_empty_zip_bytes,
    create_pdf_bytes,
)


@pytest.fixture
def client():
    return TestClient(app)


def test_invalid_file(client):
    """Sending a plain text file should return an error."""
    files = {"file": ("test.txt", create_text_bytes(), "text/plain")}
    resp = client.post("/upload", files=files)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "File type not supported"


def test_timeout(client, monkeypatch):
    """Simulate a timeout during metadata extraction."""
    def _timeout(*args, **kwargs):
        raise HTTPException(status_code=504, detail="Processing timeout")

    monkeypatch.setattr(upload, "_extract_metadata", _timeout)
    files = {"file": ("file.pdf", create_pdf_bytes(), "application/pdf")}
    resp = client.post("/upload", files=files)
    assert resp.status_code == 504
    assert resp.json()["detail"] == "Processing timeout"


def test_empty_zip(client):
    """Uploading an empty ZIP should return an error."""
    files = {"file": ("empty.zip", create_empty_zip_bytes(), "application/zip")}
    resp = client.post("/upload", files=files)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "ZIP file is empty"
