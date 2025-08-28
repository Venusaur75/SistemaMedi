import pytest

try:
    from fastapi.testclient import TestClient
    from main import app
    from api import upload
except ModuleNotFoundError:  # pragma: no cover
    pytest.skip("fastapi not installed", allow_module_level=True)

try:  # ensure PyPDF2 exists for PDF handling
    import PyPDF2  # noqa: F401
except Exception:  # pragma: no cover
    pytest.skip("PyPDF2 not installed", allow_module_level=True)

from .utils import create_report_pdf_bytes, create_pdf_bytes


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(upload, "Path", lambda p: tmp_path / p)
    return TestClient(app)


def test_ocr_pipeline_pdf(client, tmp_path):
    pdf_bytes = create_report_pdf_bytes()
    files = {"file": ("report.pdf", pdf_bytes, "application/pdf")}
    resp = client.post("/upload", files=files)
    assert resp.status_code == 200
    body = resp.json()
    report = body["report"]
    assert report["indicacao"] == "Dor no peito"
    assert report["achados"] == "Exame normal"
    assert report["conclusao"].startswith("Sem sinais")
    assert "01/02/2023" in report["datas"]

    uid = body["uuid"]
    storage_dir = tmp_path / "storage" / uid
    assert (storage_dir / "original.pdf").exists()
    assert (storage_dir / "report.json").exists()


def test_ocr_pipeline_pdf_no_headers(client):
    pdf_bytes = create_pdf_bytes()
    files = {"file": ("plain.pdf", pdf_bytes, "application/pdf")}
    resp = client.post("/upload", files=files)
    assert resp.status_code == 200
    body = resp.json()
    report = body["report"]
    assert report["indicacao"] is None
    assert report["achados"] is None
    assert report["conclusao"] is None
    assert report["datas"] == []
