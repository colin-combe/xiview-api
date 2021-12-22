import subprocess
import os
import credentials


def recreate_db():
    # drop and recreate the postgresql database

    try:
        subprocess.call("dropdb --if-exists -U %s ximzid_unittests" % credentials.username,
                        shell=True)
    except subprocess.CalledProcessError as e:
        raise e
    subprocess.call("createdb -U %s ximzid_unittests" % credentials.username, shell=True)
    schema = os.path.join(os.path.dirname(__file__), '..', 'parser', 'database',
                          'postgreSQL_schema.sql')
    subprocess.call("psql -U %s -d ximzid_unittests < %s" % (credentials.username, schema),
                    shell=True)
