from app.models.base import Base
from app.models import *
from sqlalchemy import Column, Integer, ForeignKey, ForeignKeyConstraint, Table
from sqlalchemy.types import (
    FLOAT,
    JSON,
    BOOLEAN,
    SMALLINT,
    BIGINT,
    Text,
    TIMESTAMP,
    LargeBinary
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, drop_database, create_database
from sqlalchemy.sql import func

import logging.config

logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

def create_db(connection_str):
    engine = create_engine(connection_str)
    if not database_exists(engine.url):
        create_database(engine.url)


def drop_db(connection_str):
    engine = create_engine(connection_str)
    drop_database(engine.url)


def create_schema(connection_str):
    engine = create_engine(connection_str)
    # base = declarative_base()

    # Table(
    #     "DBSequence",
    #     base.metadata,
    #     Column("id", Text, primary_key=True, nullable=False),
    #     Column("upload_id", Integer, ForeignKey("Upload.id"), primary_key=True,
    #            nullable=False, index=True),
    #     Column("accession", Text, nullable=False),
    #     Column("name", Text, nullable=True),
    #     Column("description", Text, nullable=True),
    #     Column("sequence", Text, nullable=True),
    #     quote=False
    # )
    #
    # Table(
    #     "Layout",
    #     base.metadata,
    #     Column("upload_id", Integer, ForeignKey("Upload.id"), primary_key=True, index=True, nullable=False),
    #     Column("user_id", Integer, ForeignKey("UserAccount.id"), primary_key=True, nullable=False),
    #     Column("time", TIMESTAMP, server_default=func.now(), primary_key=True, nullable=False),
    #     Column("layout", JSON, nullable=False),
    #     Column("description", Text, nullable=True),
    #     quote=False
    # )
    #
    # Table(
    #     "SearchModification",
    #     base.metadata,
    #     Column("id", BIGINT, primary_key=True, nullable=False),
    #     Column("upload_id", Integer, ForeignKey("Upload.id"), primary_key=True, nullable=False, index=True),
    #     Column("protocol_id", Text, primary_key=True, nullable=False),
    #     Column("mod_name", Text, nullable=False),
    #     Column("mass", FLOAT, nullable=False),
    #     Column("residues", Text, nullable=False),
    #     Column("specificity_rules", JSON, nullable=False),
    #     Column("fixed_mod", BOOLEAN, nullable=False),
    #     Column("accession", Text, nullable=True),
    #     Column("crosslinker_id", Text, nullable=True),
    #     ForeignKeyConstraint(
    #         ("protocol_id", "upload_id"),
    #         ("SpectrumIdentificationProtocol.id", "SpectrumIdentificationProtocol.upload_id"),
    #     ),
    #     quote=False
    # )
    #
    # Table(
    #     "Enzyme",
    #     base.metadata,
    #     Column("id", Text, primary_key=True, nullable=False),
    #     Column("upload_id", Integer, ForeignKey("Upload.id"), primary_key=True,
    #            nullable=False, index=True),
    #     Column("protocol_id", Text, nullable=False),
    #     Column("c_term_gain", Text, nullable=True),
    #     Column("min_distance", Integer, nullable=True),
    #     Column("missed_cleavages", Integer, nullable=True),
    #     Column("n_term_gain", Text, nullable=True),
    #     Column("name", Text, nullable=True),
    #     Column("semi_specific", BOOLEAN, nullable=True),
    #     Column("site_regexp", Text, nullable=True),
    #     Column("accession", Text, nullable=True),
    #     ForeignKeyConstraint(
    #         ("protocol_id", "upload_id"),
    #         ("SpectrumIdentificationProtocol.id", "SpectrumIdentificationProtocol.upload_id"),
    #     ),
    #     quote=False
    # )
    #
    # Table(
    #     "PeptideEvidence",  # equivalent of xi2 PeptidePosition Table
    #     base.metadata,
    #     Column("upload_id", Integer, ForeignKey("Upload.id"), index=True, primary_key=True,
    #            nullable=False),
    #     Column("peptide_ref", Text, primary_key=True, nullable=False, index=True),
    #     Column("dbsequence_ref", Text, primary_key=True, nullable=False),
    #     Column("pep_start", Integer, primary_key=True, nullable=False),
    #     Column("is_decoy", BOOLEAN, nullable=True),
    #     ForeignKeyConstraint(
    #         ("dbsequence_ref", "upload_id"),
    #         ("DBSequence.id", "DBSequence.upload_id"),
    #     ),
    #     ForeignKeyConstraint(
    #         ("peptide_ref", "upload_id"),
    #         ("ModifiedPeptide.id", "ModifiedPeptide.upload_id"),
    #     ),
    #     quote=False
    # )
    #
    # Table(
    #     "ModifiedPeptide",
    #     base.metadata,
    #     Column("id", Text, primary_key=True, nullable=False),
    #     Column("upload_id", Integer, ForeignKey("Upload.id"), index=True, primary_key=True,
    #            nullable=False),
    #     Column("base_sequence", Text, nullable=False),
    #     Column("mod_accessions", JSON, nullable=False),
    #     Column("mod_avg_mass_deltas", JSON, nullable=True),
    #     Column("mod_monoiso_mass_deltas", JSON, nullable=True),
    #     Column("mod_positions", JSON, nullable=False),  # 1-based with 0 = n-terminal and len(pep)+1 = C-terminal
    #     # following columns are not in xi2 db, but come out of the mzid on the <Peptide>s
    #     Column("link_site1", Integer, nullable=True),
    #     Column("link_site2", Integer, nullable=True),  # only used for storing loop links
    #     Column("crosslinker_modmass", FLOAT, nullable=True),
    #     Column("crosslinker_pair_id", Text, nullable=True),  # yes, its a string
    #     Column("crosslinker_accession", Text, nullable=True),
    #     quote=False
    # )
    #
    # Table(
    #     "Spectrum",
    #     base.metadata,
    #     Column("id", Text, primary_key=True, nullable=False),  # spectrumID from mzID
    #     Column("spectra_data_ref", Text, primary_key=True, nullable=False),
    #     Column("upload_id", Integer, ForeignKey("Upload.id"), primary_key=True, index=True,
    #            nullable=False),
    #     Column("peak_list_file_name", Text, nullable=False),
    #     Column("precursor_mz", FLOAT, nullable=False),
    #     Column("precursor_charge", SMALLINT, nullable=True),
    #     Column("mz", LargeBinary, nullable=False),
    #     Column("intensity", LargeBinary, nullable=False),
    #     Column("retention_time", FLOAT, nullable=True),
    #     quote=False
    # )
    #
    # Table(
    #     "SpectrumIdentification",
    #     base.metadata,
    #     Column("id", Text, primary_key=True, nullable=False),
    #     Column("upload_id", Integer, ForeignKey("Upload.id"), index=True, primary_key=True,
    #            nullable=False),
    #     Column("spectrum_id", Text, nullable=True),
    #     Column("spectra_data_ref", Text, nullable=True),
    #     Column("multiple_spectra_identification_id", Integer, nullable=True),
    #     Column("pep1_id", Text, nullable=False),
    #     Column("pep2_id", Text, nullable=True),
    #     Column("charge_state", Integer, nullable=True),
    #     Column("pass_threshold", BOOLEAN, nullable=False),
    #     Column("rank", Integer, nullable=False),
    #     Column("scores", JSON, nullable=True),
    #     Column("exp_mz", FLOAT, nullable=True),
    #     Column("calc_mz", FLOAT, nullable=True),
    #     Column("sil_id", Text, nullable=True),  # may be null if from csv file
    #     ForeignKeyConstraint(
    #         ["spectra_data_ref", "upload_id"],
    #         ["AnalysisCollection.spectra_data_ref",
    #          "AnalysisCollection.upload_id"],
    #     ),
    #     # Can't use this ForeignKeyConstraint, because we want to allow people to upload data
    #     # without spectra
    #     # ForeignKeyConstraint(
    #     #     ["spectrum_id", "spectra_data_ref", "upload_id"],
    #     #     ["Spectrum.id", "Spectrum.spectra_data_ref", "Spectrum.upload_id"],
    #     # ),
    #     ForeignKeyConstraint(
    #         ["pep1_id", "upload_id"],
    #         ["ModifiedPeptide.id", "ModifiedPeptide.upload_id"],
    #     ),
    #     ForeignKeyConstraint(
    #         ["pep2_id", "upload_id"],
    #         ["ModifiedPeptide.id", "ModifiedPeptide.upload_id"],
    #     ),
    #     quote=False
    # )
    #
    # Table("AnalysisCollection",
    #       base.metadata,
    #       Column("upload_id", Integer, ForeignKey("Upload.id"), index=True, primary_key=True,
    #              nullable=False),
    #       Column("spectrum_identification_list_ref", Text, primary_key=False, nullable=False),
    #       Column("spectrum_identification_protocol_ref", Text, primary_key=False, nullable=False),
    #       Column("spectra_data_ref", Text, primary_key=True, nullable=False),
    #       ForeignKeyConstraint(
    #           ["spectrum_identification_protocol_ref", "upload_id"],
    #           ["SpectrumIdentificationProtocol.id", "SpectrumIdentificationProtocol.upload_id"],
    #       ),
    #       quote=False
    #       )
    #
    # Table(
    #     "SpectrumIdentificationProtocol",
    #     base.metadata,
    #     Column("id", Text, primary_key=True, nullable=False),
    #     Column("upload_id", Integer, ForeignKey("Upload.id"), index=True, primary_key=True,
    #            nullable=False),
    #     Column("frag_tol", Text, nullable=False),
    #     Column("search_params", JSON, nullable=True),
    #     Column("analysis_software", JSON, nullable=True),
    #     Column("threshold", JSON, nullable=True),
    #     quote=False
    # )
    #
    # Table(
    #     "Upload",
    #     base.metadata,
    #     Column("id", Integer, primary_key=True, autoincrement=True, nullable=False),
    #     Column("user_id", Integer, ForeignKey("UserAccount.id"), nullable=True),
    #     Column("project_id", Text, nullable=True),
    #     Column("identification_file_name", Text, nullable=False),
    #     Column("provider", JSON, nullable=True),
    #     Column("audits", JSON, nullable=True),
    #     Column("samples", JSON, nullable=True),
    #     Column("bib", JSON, nullable=True),
    #     Column("spectra_formats", JSON, nullable=True),  # nullable=False
    #     Column("upload_time", TIMESTAMP, server_default=func.now(), nullable=False),
    #     Column("contains_crosslinks", BOOLEAN, nullable=True),  # nullable=False
    #     Column("upload_error", Text, nullable=True),  # nullable=False
    #     Column("error_type", Text, nullable=True),  # nullable=False
    #     Column("upload_warnings", JSON, nullable=True),  # nullable=False
    #     Column("identification_file_name_clean", Text, nullable=True),
    #     # Column(
    #     #     "random_id", GUID,
    #     #     server_default=text("gen_random_uuid()"),
    #     # ),
    #     quote=False
    # )
    #
    # Table(
    #     "UserAccount",
    #     base.metadata,
    #     Column("id", Integer, primary_key=True, nullable=False),
    #     Column("user_name", Text, nullable=False),
    #     Column("password", Text, nullable=False),
    #     Column("email", Text, nullable=False),
    #     Column("gdpr_token", Text, nullable=True),
    #     Column("ptoken", Text, nullable=True),
    #     Column("ptoken_timestamp", TIMESTAMP, nullable=True),
    #     Column("gdpr_timestamp", TIMESTAMP, nullable=True),
    #     quote=False
    # )

    Base.metadata.create_all(engine)
    logging.info(Base.metadata.tables)
    engine.dispose()


if __name__ == "__main__":
    try:
        from db_config_parser import get_conn_str
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            'Database credentials missing! '
            'Change default.database.ini and save as database.ini')
    conn_str = get_conn_str()
    create_db(conn_str)
    create_schema(conn_str)
