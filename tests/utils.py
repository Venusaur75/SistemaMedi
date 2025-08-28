import zipfile
from io import BytesIO

import pydicom
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, generate_uid
try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None


def create_fake_dicom_bytes() -> bytes:
    """Generate a minimal valid DICOM file in memory."""
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
