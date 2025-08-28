# SistemaMedi

## Endpoints

### POST /upload
Recebe um arquivo via `multipart/form-data` e detecta automaticamente o tipo.
Suporta arquivos **DICOM**, **ZIP**, **PDF** e **PNG/JPG**. Retorna JSON contendo o
formato detectado, o tamanho em bytes e metadados básicos extraídos.

## Interface Web

Uma interface básica em HTML/JavaScript está disponível na raiz do servidor. Ela
permite selecionar um arquivo de exame, enviá-lo ao endpoint `/upload` e exibir
o retorno JSON com metadados e campos extraídos.
