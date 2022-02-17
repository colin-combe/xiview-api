import os
from parser.writer import Table
from parser.database import PostgreSQL, SQLite
import logging
from parser.peaklistReader.PeakListWrapper import PeakListWrapper
from .db_pytest_fixtures import *
import subprocess
from .compare import compare_postgresql_dumps, compare_databases
# from .utils import recreate_db
from shutil import copyfile
import ntpath
from .parse_csv import parse_full_csv_into_postgresql

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)


def test_full_csv_parser_postgres_mgf(tmpdir, db_info, use_database, engine):
    # recreate_db()
    # file paths
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'csv_parser', 'full_csv_mgf')
    csv = os.path.join(fixtures_dir, 'PolII_XiVersion1.6.742_PSM_xiFDR1.1.27.csv')
    peaklist_zip_file = os.path.join(fixtures_dir, 'Rappsilber_CLMS_PolII_MGFs.zip')
    peak_list_folder = PeakListWrapper.unzip_peak_lists(peaklist_zip_file, out_path=tmpdir)
    fasta_file = os.path.join(fixtures_dir, 'polII-uniprot.fasta')
    # copy fasta file to tmpdir so it is being read by the parser
    copyfile(fasta_file, os.path.join(str(tmpdir), ntpath.basename(fasta_file)))

    # parse the csv file
    # id_parser = FullCsvParser(csv, str(tmpdir), peak_list_folder, PostgreSQL, logger,
    #                           db_name='ximzid_unittests', user_id=0)
    # id_parser.check_required_columns()
    # id_parser.parse()

    id_parser = parse_full_csv_into_postgresql(csv, peak_list_folder, tmpdir, logger,
                                          use_database, engine)

    with engine.connect() as conn:

        # DBSequence
        stmt = Table("DBSequence", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
                     quote=False).select()
        rs = conn.execute(stmt)
        # compare_db_sequence(rs.fetchall())

    # dump the postgresql to file
    # test_dump = os.path.join(str(tmpdir), 'test.sql')
    # cmd = "pg_dump -d ximzid_unittests -U xiadmin > " + test_dump
    # subprocess.call(cmd, shell=True)
    #
    # expected_dump = os.path.join(fixtures_dir, 'polII_db_dump.sql')
    # compare_postgresql_dumps(expected_dump, test_dump)

# def test_psql_mgf_mzid_parser(tmpdir, use_database, engine):
#     # file paths
#     fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'mzid_parser')
#     mzid = os.path.join(fixtures_dir, 'mgf_ecoli_dsso.mzid')
#     peak_list_folder = os.path.join(fixtures_dir, 'peaklist')
#
#     id_parser = parse_mzid_into_postgresql(mzid, peak_list_folder, tmpdir, logger,
#                                            use_database, engine)
#
#     with engine.connect() as conn:
#
#         # DBSequence
#         stmt = Table("DBSequence", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
#                      quote=False).select()
#         rs = conn.execute(stmt)
#         compare_db_sequence(rs.fetchall())
#
#         # Layout
#         stmt = Table("Layout", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
#                      quote=False).select()
#         rs = conn.execute(stmt)
#         assert len(rs.fetchall()) == 0
#
#         # SearchModification - parsed from <SearchModification>s
#         stmt = Table("SearchModification", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
#                      quote=False).select()
#         rs = conn.execute(stmt)
#         compare_modification(rs.fetchall())
#
#         # Enzyme - parsed from SpectrumIdentificationProtocols
#         stmt = Table("Enzyme", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
#                      quote=False).select()
#         rs = conn.execute(stmt)
#         compare_enzyme(rs.fetchall())
#
#         # PeptideEvidence
#         stmt = Table("PeptideEvidence", id_parser.writer.meta,
#                      autoload_with=id_parser.writer.engine, quote=False).select()
#         rs = conn.execute(stmt)
#         compare_peptide_evidence(rs.fetchall())
#
#         # ModifiedPeptide
#         stmt = Table("ModifiedPeptide", id_parser.writer.meta,
#                      autoload_with=id_parser.writer.engine, quote=False).select()
#         rs = conn.execute(stmt)
#         compare_modified_peptide(rs.fetchall())
#
#         # Spectrum
#         compare_spectrum_mgf(conn, peak_list_folder)
#
#         # SpectrumIdentification
#         stmt = Table("SpectrumIdentification", id_parser.writer.meta,
#                      autoload_with=id_parser.writer.engine, quote=False).select()
#         rs = conn.execute(stmt)
#         assert 22 == rs.rowcount
#         results = rs.fetchall()
#         assert results[0].id == 'SII_3_1'  # id from first <SpectrumIdentificationItem>
#         assert results[0].spectrum_id == 'index=3'  # spectrumID from <SpectrumIdentificationResult>
#         # spectraData_ref from <SpectrumIdentificationResult>
#         assert results[0].spectra_data_ref == \
#                'SD_0_recal_B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mgf'
#         # peptide_ref from <SpectrumIdentificationItem>
#         assert results[0].pep1_id == \
#                '6_VAEmetETPHLIHKVALDPLTGPMPYQGR_11_MGHAGAIIAGGKGTADEK_11_12_p1'
#         # peptide_ref from matched <SpectrumIdentificationItem> by crosslink_identification_id
#         assert results[0].pep2_id == \
#                '6_VAEmetETPHLIHKVALDPLTGPMPYQGR_11_MGHAGAIIAGGKGTADEK_11_12_p0'
#         assert results[0].charge_state == 5  # chargeState from <SpectrumIdentificationItem>
#         assert results[0].pass_threshold  # passThreshold from <SpectrumIdentificationItem>
#         assert results[0].rank == 1  # rank from <SpectrumIdentificationItem>
#         # scores parsed from score related cvParams in <SpectrumIdentificationItem>
#         assert results[0].scores == '{"xi:score": 33.814201}'
#         # experimentalMassToCharge from <SpectrumIdentificationItem>
#         assert results[0].exp_mz == 945.677359
#         # calculatedMassToCharge from <SpectrumIdentificationItem>
#         assert results[0].calc_mz == 945.6784858667701
#         # Meta columns are only parsed from csv docs
#         assert results[0].meta1 == ''
#         assert results[0].meta2 == ''
#         assert results[0].meta3 == ''
#         # ToDo: check more rows?
#
#         # SpectrumIdentificationProtocol
#         stmt = Table("SpectrumIdentificationProtocol", id_parser.writer.meta,
#                      autoload_with=id_parser.writer.engine, quote=False).select()
#         rs = conn.execute(stmt)
#         compare_spectrum_identification_protocol(rs.fetchall())
#
#         # Upload
#         stmt = Table("Upload", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
#                      quote=False).select()
#         rs = conn.execute(stmt)
#         assert 1 == rs.rowcount
#         results = rs.fetchall()
#
#         assert results[0].identification_file_name == 'mgf_ecoli_dsso.mzid'
#         assert results[0].provider == (
#             '{"id": "PROVIDER", "ContactRole": ['
#             '{"contact_ref": "PERSON_DOC_OWNER", "Role": "researcher"}]}')
#         assert results[0].audits == (
#             '{"Person": {"lastName": "Kolbowski", "firstName": "Lars", "id": "PERSON_DOC_OWNER", '
#             '"Affiliation": [{"organization_ref": "ORG_DOC_OWNER"}], '
#             '"contact address": "TIB 4/4-3 Geb\\u00e4ude 17, Aufgang 1, Raum 476 '
#             'Gustav-Meyer-Allee 25 13355 Berlin", '
#             '"contact email": "lars.kolbowski@tu-berlin.de"}, '
#             '"Organization": {"id": "ORG_DOC_OWNER", "name": "TU Berlin", '
#             '"contact name": "TU Berlin"}}'
#         )
#         assert results[0].samples == '{}'
#         assert results[0].bib == '[]'
#         assert results[0].spectra_formats == (
#             '[{"location": "recal_B190717_20_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX01_rep2.mgf", '
#             '"id": "SD_0_recal_B190717_20_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX01_rep2.mgf", '
#             '"FileFormat": "Mascot MGF format", '
#             '"SpectrumIDFormat": "multiple peak list nativeID format"}, '
#             '{"location": "recal_B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mgf", '
#             '"id": "SD_0_recal_B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mgf", '
#             '"FileFormat": "Mascot MGF format", '
#             '"SpectrumIDFormat": "multiple peak list nativeID format"}]')
#         assert results[0].contains_crosslinks
#         assert results[0].upload_error is None
#         assert results[0].error_type is None
#         assert results[0].upload_warnings == []
#         assert not results[0].deleted
#
#     engine.dispose()


# def test_links_only_csv_parser_postgres(tmpdir):
#     recreate_db()
#     # file paths
#     fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'csv_parser',
#                                 'linksonly_csv')
#     csv = os.path.join(fixtures_dir, 'results.csv')
#     fasta_file = os.path.join(fixtures_dir, 'results.fasta')
#     # copy fasta file to tmpdir so it is being read by the parser
#     copyfile(fasta_file, os.path.join(str(tmpdir), ntpath.basename(fasta_file)))
#
#     # parse the csv file
#     id_parser = LinksOnlyCsvParser(csv, str(tmpdir), None, PostgreSQL, logger,
#                                    db_name='ximzid_unittests', user_id=0)
#     id_parser.check_required_columns()
#     id_parser.parse()
#
#     # dump the postgresql to file
#     test_dump = os.path.join(str(tmpdir), 'test.sql')
#     cmd = "pg_dump -d ximzid_unittests -U xiadmin > " + test_dump
#     subprocess.call(cmd, shell=True)
#
#     expected_dump = os.path.join(fixtures_dir, 'results.sql')
#     compare_postgresql_dumps(expected_dump, test_dump)
#
#
# def test_no_peak_list_csv_parser_postgres(tmpdir):
#     recreate_db()
#     # file paths
#     fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'csv_parser',
#                                 'nopeaklist_csv')
#     csv = os.path.join(fixtures_dir, 'PolII_nopeaklist.csv')
#     fasta_file = os.path.join(fixtures_dir, 'polII-uniprot.fasta')
#     # copy fasta file to tmpdir so it is being read by the parser
#     copyfile(fasta_file, os.path.join(str(tmpdir), ntpath.basename(fasta_file)))
#
#     # parse the csv file
#     id_parser = NoPeakListsCsvParser(csv, str(tmpdir), None, PostgreSQL, logger,
#                                      db_name='ximzid_unittests', user_id=0)
#
#     # id_parser = FullCsvParser(csv, str(tmpdir), peak_list_folder, PostgreSQL, logger, user_id=0)
#     id_parser.check_required_columns()
#     id_parser.parse()
#
#     # dump the postgresql to file
#     test_dump = os.path.join(str(tmpdir), 'test.sql')
#     cmd = "pg_dump -d ximzid_unittests -U xiadmin > " + test_dump
#     subprocess.call(cmd, shell=True)
#
#     expected_dump = os.path.join(fixtures_dir, 'polII_nopeaklist_dump.sql')
#     compare_postgresql_dumps(expected_dump, test_dump)
#
#
# def test_xispec_csv_parser_mzml(tmpdir):
#     # file paths
#     fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'csv_parser', 'xispec_mzml')
#     csv = os.path.join(fixtures_dir, 'example.csv')
#     test_database = os.path.join(str(tmpdir), 'test.db')
#     peaklist_zip_file = os.path.join(fixtures_dir, 'example.mzML.zip')
#     peak_list_folder = PeakListWrapper.unzip_peak_lists(peaklist_zip_file, out_path=tmpdir)
#
#     # parse the csv file
#     id_parser = xiSPEC_CsvParser(csv, str(tmpdir), peak_list_folder, SQLite, logger,
#                                  db_name=test_database)
#     id_parser.check_required_columns()
#
#     SQLite.create_tables(id_parser.cur, id_parser.con)
#     id_parser.parse()
#
#     # connect to the databases
#     test_con = SQLite.connect(test_database)
#     test_cur = test_con.cursor()
#
#     expected_db = os.path.join(fixtures_dir, 'example.db')
#     expected_con = SQLite.connect(expected_db)
#     expected_cur = expected_con.cursor()
#
#     compare_databases(expected_cur, test_cur)
