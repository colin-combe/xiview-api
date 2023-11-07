from fastapi import APIRouter, Depends
from sqlalchemy import select, update

from app.models.dbsequence import DBSequence
from app.models.peptideevidence import PeptideEvidence
from app.models.spectrumidentification import SpectrumIdentification
from app.models.upload import Upload
from process_dataset import convert_pxd_accession_from_pride
from sqlalchemy.orm import Session
from app.routes.index import get_session
import os
import requests
import logging.config

logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

main_router = APIRouter()


@main_router.post("/parse/{px_accession}", tags=["Main"])
async def parse(px_accession: str, temp_dir: str | None = None, dont_delete: bool = False):
    if temp_dir:
        temp_dir = os.path.expanduser(temp_dir)
    else:
        temp_dir = os.path.expanduser('~/mzId_convertor_temp')
    convert_pxd_accession_from_pride(px_accession, temp_dir, dont_delete)


@main_router.get("/health-test", tags=["Main"])
async def health():
    logger.info('Checking the health-test')
    return "OK"


@main_router.get("/update-project-details", tags=["Maintenance"])
async def update_project_details(session: Session = Depends(get_session)):
    uploads = session.execute(select(Upload)).all()
    projectListToUpdate = []
    for upload in uploads:
        isNeedToUpdate = False
        # get project details from PRIDE API
        # TODO: need to move URL to a configuration variable
        px_url = 'https://www.ebi.ac.uk/pride/ws/archive/v2/projects/' + upload[0].project_id
        print('GET request to PRIDE API: ' + px_url)
        pride_response = requests.get(px_url)
        r = requests.get(px_url)
        if r.status_code == 200:
            print('PRIDE API returned status code 200')
            pride_json = pride_response.json()
            pubmedId = ''
            if len(pride_json['references']) > 0:
                pubmedId = pride_json['references'][0]['pubmedId']
            if pride_json is not None:
                if upload[0].title is None or upload[0].title != pride_json['title']:
                    isNeedToUpdate = True
                    upload[0].title = pride_json['title']
                if upload[0].description is None or upload[0].description != pride_json['projectDescription']:
                    isNeedToUpdate = True
                    upload[0].description = pride_json['projectDescription']
                if (upload[0].pubmed_id is None and pubmedId != '') or upload[0].pubmed_id != pubmedId:
                    isNeedToUpdate = True
                    upload[0].pubmed_id = pubmedId

                if isNeedToUpdate:
                    projectListToUpdate.append(upload[0])

    for upload in projectListToUpdate:
        stmt = update(Upload).where(Upload.id == upload.id).values(title=upload.title, description=upload.description,
                                                                   pubmed_id=upload.pubmed_id)
        session.execute(stmt)
    session.commit()


@main_router.get("/calculate-stats", tags=["Maintenance"])
async def calculate_stats(session: Session = Depends(get_session)):
    rows = session.query(Upload).all()
    for row in rows:
        number_of_proteins = session.query(DBSequence).filter(DBSequence.upload_id == row.id).count()
        print(f"Number of proteins: {number_of_proteins}")
        number_of_peptides = session.query(PeptideEvidence).filter(PeptideEvidence.upload_id == row.id).count()
        print(f"Number of peptides: {number_of_peptides}")
        number_of_spectra = session.query(SpectrumIdentification).filter(SpectrumIdentification.upload_id == row.id).count()
        print(f"Number of Spectra: {number_of_spectra}")
        print(".......................................")