from fastapi import APIRouter, UploadFile, File, HTTPException
import filetype
import pydicom
from pydicom.errors import InvalidDicomError
import zipfile
from io import BytesIO
from PyPDF2 import PdfReader
from PIL import Image

router = APIRouter()


def _detect_type(data: bytes) -> str:
    # Check DICOM first
    try:
        if pydicom.misc.is_dicom(BytesIO(data)):
            return 'dicom'
    except Exception:
        pass
    kind = filetype.guess(data)
    if kind is None:
        return ''
    return kind.extension.lower()


def _extract_metadata(file_type: str, data: bytes):
    meta = {}
    if file_type == 'dicom':
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
    elif file_type == 'pdf':
        reader = PdfReader(BytesIO(data))
        meta['pages'] = len(reader.pages)
    elif file_type in {'png', 'jpg', 'jpeg'}:
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
