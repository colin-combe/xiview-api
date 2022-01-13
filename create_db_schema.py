from sqlalchemy import Column, Integer, ForeignKey, ForeignKeyConstraint, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import (
    VARCHAR,
    FLOAT,
    JSON,
    BOOLEAN,
    ARRAY,
    SMALLINT,
    BIGINT,
    Text,
    TIMESTAMP,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, drop_database, create_database
from credentials import *
from sqlalchemy.sql import func


def create_db(
    host=hostname, db=database, dbuser=username, dbpassword=password
):
    engine = create_engine(f"postgresql://{dbuser}:{dbpassword}@{host}/{db}")
    if not database_exists(engine.url):
        create_database(engine.url)


def drop_db(
    host=hostname, db=database, dbuser=username, dbpassword=password
):
    engine = create_engine(f"postgresql://{dbuser}:{dbpassword}@{host}/{db}")
    drop_database(engine.url)


def create_schema(
    host=hostname, db=database, dbuser=username, dbpassword=password
):

    # Engine provided a common interface the database.
    # Here we are using the 'postgresql' driver.
    engine = create_engine(f"postgresql://{dbuser}:{dbpassword}@{host}/{db}")

    base = declarative_base()

    Table(
        "DBSequence",
        base.metadata,
        Column("id", Text, primary_key=True, nullable=False),
        Column("upload_id", UUID, ForeignKey("Upload.id"), primary_key=True, nullable=False),
        Column("accession", Text, nullable=False),
        # ToDo: why protein_?
        Column("protein_name", Text, nullable=True),
        Column("description", Text, nullable=True),
        Column("sequence", Text, nullable=True),
        quote=False
    )

    Table(
        "Layout",
        base.metadata,
        Column("upload_id", UUID, ForeignKey("Upload.id"), primary_key=True, index=True,
               nullable=False),
        Column("user_id", UUID, ForeignKey("UserAccount.id"), primary_key=True,  nullable=False),
        Column("time", TIMESTAMP, server_default=func.now(),  primary_key=True, nullable=False),
        Column("layout", JSON, nullable=False),
        Column("description", Text, nullable=True),
        quote=False
    )

    Table(
        "Modification",
        base.metadata,
        Column("id", BIGINT, primary_key=True, nullable=False),
        Column("upload_id", UUID, ForeignKey("Upload.id"), primary_key=True, nullable=False),
        Column("mod_name", Text, nullable=False),
        Column("mass", FLOAT, nullable=False),
        Column("residues", Text, nullable=False),
        Column("accession", Text, nullable=True),
        quote=False
    )

    Table(
        "PeptideEvidence",  # equivalent of xi2 PeptidePosition Table
        base.metadata,
        Column("upload_id", UUID, ForeignKey("Upload.id"), index=True, primary_key=True,
               nullable=False),
        Column("peptide_ref", Text, primary_key=True, nullable=False),
        Column("dbsequence_ref", Text, primary_key=True, nullable=False),
        # Column("protein_accession", Text, nullable=True),
        Column("pep_start", Integer, primary_key=True, nullable=False),
        Column("is_decoy", BOOLEAN, nullable=True),
        quote=False
    )

    Table(
        "ModifiedPeptide",
        base.metadata,
        Column("id", Text, primary_key=True, nullable=False),
        Column("upload_id", UUID, ForeignKey("Upload.id"), index=True, primary_key=True,
               nullable=False),
        Column("seq_mods", Text, nullable=False),
        Column("link_site", Integer, nullable=True),
        Column("crosslinker_modmass", FLOAT, nullable=True),
        Column("crosslinker_pair_id", VARCHAR, nullable=True),
        quote=False
    )

    Table(
        "Spectrum",
        base.metadata,
        Column("id", Text, primary_key=True, nullable=False),   # spectrumID from mzID
        Column("spectra_data_ref", Text, primary_key=True, nullable=False),  # ToDo: ForeignKey?
        Column("upload_id", UUID, ForeignKey("Upload.id"),  primary_key=True, index=True,
               nullable=False),
        Column("scan_id", Text, nullable=False),   # parsed scan_id ToDo: Do we need this?
        Column("peak_list_file_name", Text, nullable=False),
        Column("precursor_mz", FLOAT, nullable=False),
        Column("precursor_charge", SMALLINT, nullable=True),
        Column("frag_tol", Text, nullable=False),
        Column("mz", ARRAY(FLOAT), nullable=False),
        Column("intensity", ARRAY(FLOAT), nullable=False),
        quote=False
    )

    Table(
        "SpectrumIdentification",  # equivalent to Match table in xi2
        base.metadata,
        Column("id", Text, primary_key=True, nullable=False),
        Column("upload_id", UUID, ForeignKey("Upload.id"), index=True, primary_key=True,
               nullable=False),
        Column("spectrum_id", Text, nullable=False),
        Column("spectra_data_ref", Text, nullable=False),
        Column("pep1_id", Text, nullable=False),
        Column("pep2_id", Text, nullable=True),
        Column("charge_state", Integer, nullable=True),
        Column("pass_threshold", BOOLEAN, nullable=False),
        Column("rank", Integer, nullable=False),
        Column("ions", Text, nullable=True),
        Column("scores", JSON, nullable=True),
        Column("exp_mz", FLOAT, nullable=True),
        Column("calc_mz", FLOAT, nullable=True),
        Column("meta1", VARCHAR, server_default='', nullable=True),
        Column("meta2", VARCHAR, server_default='', nullable=True),
        Column("meta3", VARCHAR, server_default='', nullable=True),
        ForeignKeyConstraint(
            ["spectrum_id", "spectra_data_ref", "upload_id"],
            ["Spectrum.id", "Spectrum.spectra_data_ref", "Spectrum.upload_id"],
        ),
        ForeignKeyConstraint(
            ["pep1_id", "upload_id"],
            ["ModifiedPeptide.id", "ModifiedPeptide.upload_id"],
        ),
        ForeignKeyConstraint(
            ["pep2_id", "upload_id"],
            ["ModifiedPeptide.id", "ModifiedPeptide.upload_id"],
        ),
        quote=False
    )

    Table(
        "Upload",
        base.metadata,
        Column("id", UUID, primary_key=True, nullable=False),
        Column("user_id", UUID, ForeignKey("UserAccount.id"), nullable=False),
        Column("identification_filename", Text, nullable=False),
        Column("peak_list_file_names", JSON, nullable=True),
        Column("analysis_software", JSON, nullable=True),
        Column("provider", JSON, nullable=True),
        Column("audits", JSON, nullable=True),
        Column("samples", JSON, nullable=True),
        Column("analyses", JSON, nullable=True),
        Column("protocol", JSON, nullable=True),
        Column("bib", JSON, nullable=True),
        Column("spectra_formats", JSON, nullable=True),  # nullable=False
        Column("upload_time", TIMESTAMP, server_default=func.now(), nullable=False),
        Column("contains_crosslinks", BOOLEAN, nullable=True),  # nullable=False
        Column("upload_error", Text, nullable=True),  # nullable=False
        Column("error_type", Text, nullable=True),  # nullable=False
        Column("upload_warnings", JSON, nullable=True),  # nullable=False
        Column("deleted", BOOLEAN, server_default='false', nullable=False),
        Column("ident_count", BIGINT, nullable=True),  # nullable=False
        Column("ident_file_size", BIGINT, nullable=True),  # nullable=False
        Column("zipped_peak_list_file_size", VARCHAR, nullable=True),  # nullable=False
        quote=False
    )

    Table(
        "UserAccount",
        base.metadata,
        Column("id", UUID, primary_key=True, nullable=False),
        Column("user_name", VARCHAR, nullable=False),
        Column("password", VARCHAR, nullable=False),
        Column("email", VARCHAR, nullable=False),
        Column("gdpr_token", VARCHAR, nullable=True),
        Column("ptoken", VARCHAR, nullable=True),
        Column("ptoken_timestamp", TIMESTAMP, nullable=True),
        Column("gdpr_timestamp", TIMESTAMP, nullable=True),
        quote=False
    )

    base.metadata.create_all(engine)
    engine.dispose()


if __name__ == "__main__":
    create_db()
    create_schema()
