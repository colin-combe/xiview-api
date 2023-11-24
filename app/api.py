from fastapi import FastAPI, HTTPException

from app.routes.pride import pride_router

app = FastAPI(openapi_url="/pride/archive/xiview/ws/api/openapi.json", docs_url="/pride/archive/xiview/ws/api/docs")


app.include_router(pride_router, prefix="/pride/archive/xiview/ws/")
