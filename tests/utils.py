import subprocess
import os


def recreate_db():
    # drop and recreate the postgresql database
    if subprocess.call("dropdb --if-exists -U xiadmin xitest", shell=True) != 0:
        raise subprocess.CalledProcessError
    if subprocess.call("createdb -U xiadmin xitest", shell=True) != 0:
        raise subprocess.CalledProcessError
    schema = os.path.join(os.path.dirname(__file__), '..', 'parser', 'database',
                          'postgreSQL_schema.sql')
    subprocess.call("psql -U xiadmin -d xitest < " + schema, shell=True)
