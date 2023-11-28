from fastapi import FastAPI, HTTPException

from app.routes.pride import pride_router

app = FastAPI(title="Xi-MzIdentML-Converter WS",
              description="This is an API to crosslinking archive",
              version="0.0.1",
              license_info={
                  "name": "Apache 2.0",
                  "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
              },
              openapi_url="/pride/archive/xiview/ws/api/openapi.json",
              docs_url="/pride/archive/xiview/ws/api/docs")


app.include_router(pride_router, prefix="/pride/archive/xiview/ws")
