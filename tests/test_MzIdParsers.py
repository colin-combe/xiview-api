import credentials
from parser import MzIdParser
import os
from parser.database import PostgreSQL, SQLite
import logging
import subprocess
from .compare import compare_postgresql_dumps, compare_databases
from .utils import recreate_db


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)


def test_mzid_parser_postgres_mgf(tmpdir):
    recreate_db()
    # file paths
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'mzid_parser')
    mzid = os.path.join(fixtures_dir, 'mgf_ecoli_dsso.mzid')
    peak_list_folder = os.path.join(fixtures_dir, 'peaklist')

    # parse the mzid file
    id_parser = MzIdParser.MzIdParser(mzid, str(tmpdir), peak_list_folder, PostgreSQL, logger,
                                      db_name='ximzid_unittests', user_id=0)
    id_parser.initialise_mzid_reader()
    id_parser.parse()

    # dump the postgresql to file
    test_dump = os.path.join(str(tmpdir), 'test.sql')
    cmd = "pg_dump -d ximzid_unittests -U %s > " % credentials.username + test_dump
    subprocess.call(cmd, shell=True)

    expected_dump = os.path.join(fixtures_dir, 'mgf_ecoli_dsso_db_dump.sql')
    compare_postgresql_dumps(expected_dump, test_dump)


def test_mzid_parser_postgres_mzml(tmpdir):
    recreate_db()
    # file paths
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'mzid_parser')
    mzid = os.path.join(fixtures_dir, 'mzml_ecoli_dsso.mzid')
    peak_list_folder = os.path.join(fixtures_dir, 'peaklist')

    # parse the mzid file
    id_parser = MzIdParser.MzIdParser(mzid, str(tmpdir), peak_list_folder, PostgreSQL, logger,
                                      db_name='ximzid_unittests', user_id=0)
    id_parser.initialise_mzid_reader()
    id_parser.parse()

    # dump the postgresql to file
    test_dump = os.path.join(str(tmpdir), 'test.sql')
    cmd = "pg_dump -d ximzid_unittests -U %s > " % credentials.username + test_dump
    subprocess.call(cmd, shell=True)

    expected_dump = os.path.join(fixtures_dir, 'mzml_ecoli_dsso_db_dump.sql')
    compare_postgresql_dumps(expected_dump, test_dump)


def test_xispec_mzid_parser_mzml(tmpdir):
    # file paths
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'mzid_parser')
    mzid = os.path.join(fixtures_dir, 'mzml_ecoli_dsso.mzid')
    peak_list_folder = os.path.join(fixtures_dir, 'peaklist')
    test_database = os.path.join(str(tmpdir), 'test.db')


    # parse the mzid file
    id_parser = MzIdParser.xiSPEC_MzIdParser(mzid, str(tmpdir), peak_list_folder, SQLite, logger,
                                             db_name=test_database)

    id_parser.initialise_mzid_reader()
    SQLite.create_tables(id_parser.cur, id_parser.con)
    id_parser.parse()

    # connect to the databases
    test_con = SQLite.connect(test_database)
    test_cur = test_con.cursor()

    expected_db = os.path.join(fixtures_dir, 'mzml_ecoli_dsso_sqlite.db')
    expected_con = SQLite.connect(expected_db)
    expected_cur = expected_con.cursor()

    compare_databases(expected_cur, test_cur)


def test_xispec_mzid_parser_mgf(tmpdir):
    # file paths
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'mzid_parser')
    mzid = os.path.join(fixtures_dir, 'mgf_ecoli_dsso.mzid')
    peak_list_folder = os.path.join(fixtures_dir, 'peaklist')
    test_database = os.path.join(str(tmpdir), 'test.db')

    # parse the mzid file
    id_parser = MzIdParser.xiSPEC_MzIdParser(mzid, str(tmpdir), peak_list_folder, SQLite, logger,
                                             db_name=test_database)

    id_parser.initialise_mzid_reader()
    SQLite.create_tables(id_parser.cur, id_parser.con)
    id_parser.parse()

    # connect to the databases
    test_con = SQLite.connect(test_database)
    test_cur = test_con.cursor()

    expected_db = os.path.join(fixtures_dir, 'mgf_ecoli_dsso_sqlite.db')
    expected_con = SQLite.connect(expected_db)
    expected_cur = expected_con.cursor()

    compare_databases(expected_cur, test_cur)
