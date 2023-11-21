from fastapi import FastAPI, HTTPException

from app.routes.pride import pride_router
from app.routes.pdb import pdb_dev_router

app = FastAPI(openapi_url="/pride/archive/xiview/xi-converter/api/openapi.json", docs_url="/pride/archive/xiview/xi-converter/api/docs")


app.include_router(pride_router, prefix="/pride/archive/xiview/xi-converter")
app.include_router(pdb_dev_router, prefix="/pride/archive/pdbdev")
