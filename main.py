from fastapi import FastAPI
from api.upload import router as upload_router

app = FastAPI(title="SistemaMedi API")

app.include_router(upload_router)
