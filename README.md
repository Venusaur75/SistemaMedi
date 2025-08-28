# SistemaMedi

## Endpoints

### POST /upload
Recebe um arquivo via `multipart/form-data` e detecta automaticamente o tipo.
Suporta arquivos **DICOM**, **ZIP**, **PDF** e **PNG/JPG**. Retorna JSON contendo o
formato detectado, o tamanho em bytes e metadados básicos extraídos.
