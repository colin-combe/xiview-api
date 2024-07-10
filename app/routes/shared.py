import functools
import re
import os
import logging.config
import time

import psycopg2
from configparser import ConfigParser
from fastapi import APIRouter, Depends, status
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from db_config_parser import security_API_key

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def log_execution_time_async(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logging.info(f'"{func.__name__}" executed in {execution_time:.2f} seconds')
        return result
    return wrapper

@log_execution_time_async
async def get_most_recent_upload_ids(pxid, file=None):

    """
    Get the most recent upload ids for a project/file.

    :param pxid: identifier of a project,
        for ProteomeXchange projects this is the PXD****** accession
    :param file: name of the file
    :return: upload ids
    """

    conn = None
    upload_ids = None
    try:
        # connect to the PostgreSQL server
        # logger.info('Connecting to the PostgreSQL database...')
        conn = await get_db_connection()
        cur = conn.cursor()
        if file:
            filename_clean = re.sub(r'[^0-9a-zA-Z-]+', '-', file)
            query = """SELECT id FROM upload 
                    WHERE project_id = %s AND identification_file_name_clean = %s 
                    ORDER BY upload_time DESC LIMIT 1;"""
            # logger.debug(sql)
            cur.execute(query, [pxid, filename_clean])

            upload_ids = [cur.fetchone()[0]]
            if upload_ids is None:
                return None  # jsonify({"error": "No data found"}), 404
            # logger.info("finished")
            # close the communication with the PostgreSQL
            cur.close()
        else:
            query = """SELECT u.id
                        FROM upload u
                        where u.upload_time = 
                            (select max(upload_time) from upload 
                            where project_id = u.project_id 
                            and identification_file_name = u.identification_file_name )
                        and u.project_id = %s;"""
            # logger.debug(sql)
            cur.execute(query, [pxid])
            upload_ids = cur.fetchall()
            if upload_ids is None:
                return None  # jsonify({"error": "No data found"}), 404
            # logger.info("finished")
            # close the communication with the PostgreSQL
            cur.close()

    except (Exception, psycopg2.DatabaseError) as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()

    return upload_ids


async def get_db_connection():
    config = os.environ.get('DB_CONFIG', 'database.ini')

    # https://www.postgresqltutorial.com/postgresql-python/connect/
    async def parse_database_info(filename, section='postgresql'):
        # create a parser
        parser = ConfigParser()
        # read config file
        parser.read(filename)

        # get section, default to postgresql
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))

        return db

    # read connection information
    db_info = await parse_database_info(config)
    # logger.debug('Getting DB connection...')
    conn = psycopg2.connect(**db_info)
    return conn


def get_api_key(key: str = Security(api_key_header)) -> str:

    if key == security_API_key():
        return key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )
