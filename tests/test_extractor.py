import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ocr.extractor import extract_fields


def test_extract_from_text():
    data = (
        "Indicação: Dor no peito\n"
        "Achados: Exame normal\n"
        "Conclusão: Sem sinais\n"
        "Data 01/02/2023 e 03-02-2024"
    ).encode("utf-8")
    result = extract_fields(data, "txt")
    assert result["indicacao"] == "Dor no peito"
    assert result["achados"] == "Exame normal"
    assert result["conclusao"].startswith("Sem sinais")
    assert "01/02/2023" in result["datas"]
    assert "03-02-2024" in result["datas"]
