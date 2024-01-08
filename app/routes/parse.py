import base64
import configparser
import traceback

from fastapi import APIRouter, Depends
from fastapi import HTTPException, Security
from fastapi.params import Body
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.models.upload import Upload
from app.routes.shared import get_api_key
from db_config_parser import get_conn_str
from index import get_session
from sqlalchemy import Table, Enum, MetaData, create_engine
import logging.config

from parser.writer import Writer

logger = logging.getLogger(__name__)
writer = Writer(get_conn_str())
engine = create_engine(get_conn_str())
meta = MetaData()

parser_router = APIRouter()
config = configparser.ConfigParser()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

class TableNamesEnum(str, Enum):
    """Enumeration of Table names"""
    analysiscollection = "analysiscollection"
    dbsequence ="dbsequence"
    enzyme = "enzyme"
    modifiedpeptide ="modifiedpeptide"
    peptideevidence ="peptideevidence"
    searchmodification ="searchmodification"
    spectrum ="spectrum"
    spectrumidentification ="spectrumidentification"
    spectrumidentificationprotocol ="spectrumidentificationprotocol"
    upload = "upload"
    projectdetail = "projectdetail"
    projectsubdetail = "projectsubdetail"

@parser_router.post("/write_data", tags=["Parser"])
async def write_data(
        table: TableNamesEnum = Body(..., description="table name", embeded=True),
        data = Body(..., description="table data", embeded=True),
        api_key: str = Security(get_api_key),
        session: Session = Depends(get_session)):
        """
        Insert data into table.

        :param session:
        :param api_key:
        :param table: (str) Table name
        :param data: (list dict) data to insert.
        """
        try:
            if table==TableNamesEnum.spectrum:
                print("spectrum table")
                i=0
                for spectra in data:
                    spectra["mz"] =  base64.b64decode(spectra["mz"])
                    spectra["intensity"] =  base64.b64decode(spectra["intensity"])
                    data[i] = spectra
                    i+=1

            table = Table(table, meta, autoload_with=engine)
            with engine.connect() as conn:
                statement = table.insert().values(data)
                result = conn.execute(statement)
                conn.commit()
                conn.close()
            return result

        except Exception as e:
            print(f"Caught an exception: {e}")
            traceback.print_exc()
        finally:
            session.close()
        return result

@parser_router.post("/write_new_upload", tags=["Parser"])
def write_new_upload(
        table: TableNamesEnum = Body(..., description="table name", embeded=True),
        data: dict = Body(..., description="table data", embeded=True),
        api_key: str = Security(get_api_key),
        session: Session = Depends(get_session)):
    try:
        new_upload = Upload(**data)
        session.add(new_upload)
        session.commit()
        session.close()
        return new_upload.id
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@parser_router.post("/write_mzid_info", tags=["Admin"])
def write_mzid_info(analysis_software_list=Body(..., embeded=True),
                    spectra_formats=Body(..., embeded=True),
                    provider=Body(..., embeded=True),
                    audits=Body(..., embeded=True),
                    samples=Body(..., embeded=True),
                    bib=Body(..., embeded=True),
                    upload_id:int=None,
                    api_key: str = Security(get_api_key),
                    session: Session = Depends(get_session)):
    """
    Update Upload row with mzid info.
    :param upload_id:
    :param analysis_software_list:
    :param session:
    :param api_key:
    :param spectra_formats:
    :param provider:
    :param audits:
    :param samples:
    :param bib:
    :return:
    """
    upload = Table("upload", meta, autoload_with=engine, quote=False)
    stmt = upload.update().where(upload.c.id == str(upload_id)).values(
            analysis_software_list=analysis_software_list,
            spectra_formats=spectra_formats,
            provider=provider,
            audit_collection=audits,
            analysis_sample_collection=samples,
            bib=bib
        )
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()

@parser_router.post("/write_other_info", tags=["Parser"])
def write_other_info(contains_crosslinks = Body(..., description="contains_crosslinks", embeded=True),
                     upload_warnings = Body(..., description="upload_warnings", embeded=True),
                     upload_id:int=None,
                     api_key: str = Security(get_api_key),
                     session: Session = Depends(get_session)):
    """
    Update Upload row with remaining info.

    :param session:
    :param upload_id:
    :param api_key:
    :param contains_crosslinks:
    :param upload_warnings:
    :return:
    """

    upload = Table("upload", meta, autoload_with=engine, quote=False)
    with engine.connect() as conn:
        stmt = upload.update().where(upload.c.id == str(upload_id)).values(
                contains_crosslinks=contains_crosslinks,
                upload_warnings=upload_warnings,
            )
        conn.execute(stmt)
        conn.commit()
