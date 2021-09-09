from parser import FullCsvParser, NoPeakListsCsvParser, LinksOnlyCsvParser, xiSPEC_CsvParser
import os
from parser.database import PostgreSQL, SQLite
import logging
from parser.peaklistReader.PeakListWrapper import PeakListWrapper
import subprocess
from compare import compare_postgresql_dumps, compare_databases
from utils import recreate_db
from shutil import copyfile
import ntpath


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)


def test_full_csv_parser_postgres_mgf(tmpdir):
    recreate_db()
    # file paths
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'csv_parser', 'full_csv_mgf')
    csv = os.path.join(fixtures_dir, 'PolII_XiVersion1.6.742_PSM_xiFDR1.1.27.csv')
    peaklist_zip_file = os.path.join(fixtures_dir, 'Rappsilber_CLMS_PolII_MGFs.zip')
    peak_list_folder = PeakListWrapper.unzip_peak_lists(peaklist_zip_file, out_path=tmpdir)
    fasta_file = os.path.join(fixtures_dir, 'polII-uniprot.fasta')
    # copy fasta file to tmpdir so it is being read by the parser
    copyfile(fasta_file, os.path.join(str(tmpdir), ntpath.basename(fasta_file)))

    # parse the csv file
    id_parser = FullCsvParser(csv, str(tmpdir), peak_list_folder, PostgreSQL, logger, user_id=0)
    id_parser.check_required_columns()
    id_parser.parse()

    # dump the postgresql to file
    test_dump = os.path.join(str(tmpdir), 'test.sql')
    cmd = "pg_dump -d xitest -U xiadmin > " + test_dump
    subprocess.call(cmd, shell=True)

    expected_dump = os.path.join(fixtures_dir, 'polII_db_dump.sql')
    compare_postgresql_dumps(expected_dump, test_dump)


def test_links_only_csv_parser_postgres(tmpdir):
    recreate_db()
    # file paths
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'csv_parser',
                                'linksonly_csv')
    csv = os.path.join(fixtures_dir, 'NPC.csv')
    fasta_file = os.path.join(fixtures_dir, 'NPC.fasta')
    # copy fasta file to tmpdir so it is being read by the parser
    copyfile(fasta_file, os.path.join(str(tmpdir), ntpath.basename(fasta_file)))

    # parse the csv file
    id_parser = LinksOnlyCsvParser(csv, str(tmpdir), None, PostgreSQL, logger, user_id=0)
    id_parser.check_required_columns()
    id_parser.parse()

    # dump the postgresql to file
    test_dump = os.path.join(str(tmpdir), 'test.sql')
    cmd = "pg_dump -d xitest -U xiadmin > " + test_dump
    subprocess.call(cmd, shell=True)

    expected_dump = os.path.join(fixtures_dir, 'NPC.sql')
    compare_postgresql_dumps(expected_dump, test_dump)


def test_no_peak_list_csv_parser_postgres(tmpdir):
    recreate_db()
    # file paths
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'csv_parser',
                                'nopeaklist_csv')
    csv = os.path.join(fixtures_dir, 'PolII_nopeaklist.csv')
    fasta_file = os.path.join(fixtures_dir, 'polII-uniprot.fasta')
    # copy fasta file to tmpdir so it is being read by the parser
    copyfile(fasta_file, os.path.join(str(tmpdir), ntpath.basename(fasta_file)))

    # parse the csv file
    id_parser = NoPeakListsCsvParser(csv, str(tmpdir), None, PostgreSQL, logger, user_id=0)

    # id_parser = FullCsvParser(csv, str(tmpdir), peak_list_folder, PostgreSQL, logger, user_id=0)
    id_parser.check_required_columns()
    id_parser.parse()

    # dump the postgresql to file
    test_dump = os.path.join(str(tmpdir), 'test.sql')
    cmd = "pg_dump -d xitest -U xiadmin > " + test_dump
    subprocess.call(cmd, shell=True)

    expected_dump = os.path.join(fixtures_dir, 'polII_nopeaklist_dump.sql')
    compare_postgresql_dumps(expected_dump, test_dump)


def test_xispec_csv_parser_mzml(tmpdir):
    # file paths
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'csv_parser', 'xispec_mzml')
    csv = os.path.join(fixtures_dir, 'example.csv')
    test_database = os.path.join(str(tmpdir), 'test.db')
    peaklist_zip_file = os.path.join(fixtures_dir, 'example.mzML.zip')
    peak_list_folder = PeakListWrapper.unzip_peak_lists(peaklist_zip_file, out_path=tmpdir)

    # parse the csv file
    id_parser = xiSPEC_CsvParser(csv, str(tmpdir), peak_list_folder, SQLite, logger,
                                 db_name=test_database)
    id_parser.check_required_columns()

    SQLite.create_tables(id_parser.cur, id_parser.con)
    id_parser.parse()

    # connect to the databases
    test_con = SQLite.connect(test_database)
    test_cur = test_con.cursor()

    expected_db = os.path.join(fixtures_dir, 'example.db')
    expected_con = SQLite.connect(expected_db)
    expected_cur = expected_con.cursor()

    compare_databases(expected_cur, test_cur)
