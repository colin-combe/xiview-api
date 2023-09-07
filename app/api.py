from fastapi import FastAPI, HTTPException
# from app.routes.dbsequence import DBSequence_router
from app.routes.main import main_router

app = FastAPI()

# app.include_router(DBSequence_router)
app.include_router(main_router)
