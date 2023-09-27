from fastapi import FastAPI, HTTPException

from app.routes.main import main_router

app = FastAPI(openapi_url="/api/openapi.json", docs_url="/api/docs")


app.include_router(main_router, prefix="/api")
