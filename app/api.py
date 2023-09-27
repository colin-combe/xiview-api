from fastapi import FastAPI, HTTPException

from app.routes.main import main_router

app = FastAPI(openapi_url="/xiview/xi-converter/api/openapi.json", docs_url="/xiview/xi-converter/api/docs")


app.include_router(main_router, prefix="/xiview/xi-converter")
