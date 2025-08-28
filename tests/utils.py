import zipfile
from io import BytesIO

try:
    import pydicom
    from pydicom.dataset import Dataset, FileMetaDataset
    from pydicom.uid import ExplicitVRLittleEndian, generate_uid
except Exception:  # pragma: no cover - optional dependency
    pydicom = None
    Dataset = FileMetaDataset = None
    ExplicitVRLittleEndian = generate_uid = None
try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None


def create_fake_dicom_bytes() -> bytes:
    """Generate a minimal valid DICOM file in memory."""
    if pydicom is None:  # pragma: no cover - dependency not installed
        return b""
    meta = FileMetaDataset()
    meta.MediaStorageSOPClassUID = generate_uid()
    meta.MediaStorageSOPInstanceUID = generate_uid()
    meta.TransferSyntaxUID = ExplicitVRLittleEndian

    ds = Dataset()
    ds.PatientName = "Test"
    ds.Rows = 1
    ds.Columns = 1
    ds.file_meta = meta
    ds.is_little_endian = True
    ds.is_implicit_VR = False

    buffer = BytesIO()
    ds.save_as(buffer, write_like_original=False)
    return buffer.getvalue()


def create_empty_zip_bytes() -> bytes:
    """Create bytes for an empty ZIP archive."""
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w"):
        pass
    return buffer.getvalue()


def create_pdf_bytes() -> bytes:
    """Create minimal PDF bytes with just a header and EOF marker."""
    return b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF"


def create_report_pdf_bytes() -> bytes:
    """Create a simple one-page PDF containing diagnostic text."""
    lines = [
        "Indicação: Dor no peito",
        "Achados: Exame normal",
        "Conclusão: Sem sinais",
        "Data: 01/02/2023",
    ]

    def _escape(txt: str) -> str:
        return txt.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    content = "\n".join(lines)
    content = _escape(content)
    stream = f"BT /F1 12 Tf 50 750 Td ({content}) Tj ET"
    length = len(stream.encode("latin-1"))

    objects = [
        "1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj",
        "2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj",
        "3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj",
        f"4 0 obj<< /Length {length} >>stream\n{stream}\nendstream\nendobj",
        "5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj",
    ]

    pdf = "%PDF-1.4\n"
    offsets = []
    for obj in objects:
        offsets.append(len(pdf.encode("latin-1")))
        pdf += obj + "\n"
    xref_start = len(pdf.encode("latin-1"))

    xref = "xref\n0 6\n0000000000 65535 f \n"
    for off in offsets:
        xref += f"{off:010} 00000 n \n"
    trailer = "trailer<< /Size 6 /Root 1 0 R >>\nstartxref\n" + str(xref_start) + "\n%%EOF"

    return (pdf + xref + trailer).encode("latin-1")


def create_image_bytes(format: str = "PNG") -> bytes:
    """Create bytes for a simple image."""
    if Image is None:
        return b""
    image = Image.new("RGB", (10, 10), color="red")
    buffer = BytesIO()
    image.save(buffer, format=format)
    return buffer.getvalue()


def create_text_bytes() -> bytes:
    """Create bytes for a plain text file."""
    return b"example text"
