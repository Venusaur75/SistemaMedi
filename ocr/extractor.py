import re
from io import BytesIO
from typing import Dict, List

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None
try:
    from PyPDF2 import PdfReader
except Exception:  # pragma: no cover - handle missing dependency
    PdfReader = None


def _ocr_images(images: List) -> str:
    try:
        import pytesseract
    except Exception:
        return ""
    texts = []
    for img in images:
        texts.append(pytesseract.image_to_string(img, lang="por"))
    return "\n".join(texts)


def extract_fields(data: bytes, file_type: str) -> dict:
    """
    Extract structured fields from provided file data.

    Parameters
    ----------
    data: bytes
        Raw file bytes.
    file_type: str
        File extension such as ``pdf`` or ``png``.

    Returns
    -------
    dict
        Dictionary containing the sections "indicacao", "achados",
        "conclusao" and a list of all dates found in the document.
    """
    text = ""
    if file_type.lower() == "pdf" and PdfReader is not None:
        reader = PdfReader(BytesIO(data))
        text = "".join(page.extract_text() or "" for page in reader.pages)
        if not text.strip():
            try:
                from pdf2image import convert_from_bytes
            except Exception:
                convert_from_bytes = None
            if convert_from_bytes is not None:
                images = convert_from_bytes(data)
                text = _ocr_images(images)
    elif file_type.lower() in {"png", "jpg", "jpeg"} and Image is not None:
        image = Image.open(BytesIO(data))
        text = _ocr_images([image])
    else:
        text = data.decode("utf-8", errors="ignore")

    sections = {"indicacao": "", "achados": "", "conclusao": ""}
    header_pattern = (
        r"(Indicação|Achados|Conclusão)\s*:?(.*?)(?=\n(?:Indicação|Achados|Conclusão)\s*:|\n{2,}|\Z)"
    )
    key_map = {
        "indicação": "indicacao",
        "achados": "achados",
        "conclusão": "conclusao",
    }
    for match in re.finditer(header_pattern, text, flags=re.IGNORECASE | re.DOTALL):
        header = match.group(1).lower()
        content = match.group(2).strip()
        key = key_map.get(header, header)
        sections[key] = content

    date_pattern = r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
    dates = re.findall(date_pattern, text)

    return {**sections, "datas": dates}
