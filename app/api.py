from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.routes.pride import pride_router
from app.routes.pdbdev import pdbdev_router
from app.routes.xiview import xiview_data_router
from app.routes.parse import parser_router
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI(title="xi-mzidentml-converter ws",
              description="This is an API to crosslinking archive",
              version="0.0.1",
                contact={
                  "name": "PRIDE Team",
                  "url": "https://www.ebi.ac.uk/pride/",
                  "email": "pride-support@ebi.ac.uk",
              },
              license_info={
                  "name": "Apache 2.0",
                  "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
              },
              openapi_url="/pride/ws/archive/crosslinking/openapi.json",
              docs_url="/pride/ws/archive/crosslinking/docs")

# Set up CORS middleware
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Handles GZip responses for any request that includes "gzip" in the "Accept-Encoding" header.
# The middleware will handle both standard and streaming responses.
# Do not GZip responses that are smaller than this minimum size in bytes,
# Tier 4 Network level compression, no need to worry at Tier 7(HTTPS) level
# app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(pride_router, prefix="/pride/ws/archive/crosslinking")
app.include_router(pdbdev_router, prefix="/pride/ws/archive/crosslinking/pdbdev")
app.include_router(xiview_data_router, prefix="/pride/ws/archive/crosslinking/data")
app.include_router(parser_router, prefix="/pride/ws/archive/crosslinking/parse")

