from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.routes.index import get_session
from process_dataset import convert_pxd_accession_from_pride
import os


main_router = APIRouter()


@main_router.get("/parse/{px_accession}", tags=["Main"])
async def parse(px_accession: str, temp_dir: str | None = None, dont_delete: bool = False,
                session: Session = Depends(get_session)):
    if temp_dir:
        temp_dir = os.path.expanduser(temp_dir)
    else:
        temp_dir = os.path.expanduser('~/mzId_convertor_temp')
    convert_pxd_accession_from_pride(px_accession, temp_dir, dont_delete)


@main_router.get("/health-test", tags=["Main"])
async def health():
    return "OK"
