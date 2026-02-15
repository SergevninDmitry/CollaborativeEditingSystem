from fastapi import FastAPI
from domains.versions.router import router as versions_router

app = FastAPI(title="Version Service")

app.include_router(versions_router, prefix="/versions")
