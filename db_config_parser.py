from configparser import ConfigParser
import os


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


def get_conn_str():
    config = os.environ.get('DB_CONFIG', 'database.ini')
    db_info = parse_database_info(config)
    hostname = db_info.get("host")
    database = db_info.get("database")
    username = db_info.get("user")
    password = db_info.get("password")
    port = db_info.get("port")
    conn_str = f"postgresql://{username}:{password}@{hostname}:{port}/{database}"
    return conn_str
