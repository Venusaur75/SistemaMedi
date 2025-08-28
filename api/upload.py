from fastapi import APIRouter, UploadFile, File, HTTPException
import zipfile
from io import BytesIO
try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None

# Optional dependencies
try:
    import filetype
except Exception:  # pragma: no cover
    filetype = None

try:
    import pydicom
    from pydicom.errors import InvalidDicomError
except Exception:  # pragma: no cover
    pydicom = None
    class InvalidDicomError(Exception):
        pass

try:
    from PyPDF2 import PdfReader
except Exception:  # pragma: no cover
    PdfReader = None

router = APIRouter()


def _detect_type(data: bytes) -> str:
    # Check DICOM first
    if pydicom is not None:
        try:
            if pydicom.misc.is_dicom(BytesIO(data)):
                return 'dicom'
        except Exception:
            pass
    if filetype is not None:
        kind = filetype.guess(data)
        if kind is not None:
            return kind.extension.lower()
    # Fallback signatures
    if data.startswith(b'%PDF'):
        return 'pdf'
    if data.startswith(b'\x50\x4b\x03\x04'):
        return 'zip'
    if data.startswith(b'\x89PNG'):
        return 'png'
    if data[0:2] == b'\xff\xd8':
        return 'jpg'
    return ''


def _extract_metadata(file_type: str, data: bytes):
    meta = {}
    if file_type == 'dicom' and pydicom is not None:
        try:
            ds = pydicom.dcmread(BytesIO(data))
            meta = {
                'patient': getattr(ds, 'PatientName', None),
                'modality': getattr(ds, 'Modality', None),
                'dimensions': f"{getattr(ds, 'Rows', '?')}x{getattr(ds, 'Columns', '?')}"
            }
        except InvalidDicomError:
            raise HTTPException(status_code=400, detail='Invalid DICOM file')
    elif file_type == 'zip':
        with zipfile.ZipFile(BytesIO(data)) as zf:
            names = zf.namelist()
            if not names:
                raise HTTPException(status_code=400, detail='ZIP file is empty')
            meta['files'] = names
    elif file_type == 'pdf' and PdfReader is not None:
        reader = PdfReader(BytesIO(data))
        meta['pages'] = len(reader.pages)
    elif file_type in {'png', 'jpg', 'jpeg'} and Image is not None:
        image = Image.open(BytesIO(data))
        meta['width'], meta['height'] = image.size
    else:
        raise HTTPException(status_code=400, detail='Unsupported file type')
    return meta


@router.post('/upload')
async def upload(file: UploadFile = File(...)):
    data = await file.read()
    size = len(data)
    file_type = _detect_type(data)
    if file_type == '' or file_type not in {'dicom', 'zip', 'pdf', 'png', 'jpg', 'jpeg'}:
        raise HTTPException(status_code=400, detail='File type not supported')
    metadata = _extract_metadata(file_type, data)
    return {'type': file_type, 'size': size, 'metadata': metadata}
