import logging.config
import os
import re
from configparser import ConfigParser

import psycopg2

logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)


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
        conn = get_db_connection()
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
        logger.error(e)
    finally:
        if conn is not None:
            conn.close()
            logger.debug('Database connection closed.')

    return upload_ids


def get_db_connection():
    config = os.environ.get('DB_CONFIG', 'database.ini')

    # https://www.postgresqltutorial.com/postgresql-python/connect/
    def parse_database_info(filename, section='postgresql'):
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
    db_info = parse_database_info(config)
    # logger.debug('Getting DB connection...')
    conn = psycopg2.connect(**db_info)
    return conn
