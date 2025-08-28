from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.upload import router as upload_router

app = FastAPI(title="SistemaMedi API")

app.include_router(upload_router)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
