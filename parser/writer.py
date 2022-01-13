from uuid import uuid4
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy import Table as SATable
from sqlalchemy.dialects.postgresql import insert
# from sqlalchemy.sql.expression import bindparam
from sqlalchemy.exc import IntegrityError, NoResultFound
import numpy as np
import os


def Table(name, *args, **kw):
    """Return an SQLAlchemy table but that uses the lower case table name.
    This is a workaround for the "quote=False" argument not working properly for the postgresql
    dialect in SQLAlchemy.
    :param name: name of the table - will be forwarded as lower case string.
    """
    return SATable(name.lower(), *args, **kw)


class Writer:
    """
    Write results to database
    # Implementation of a ResultWriter which outputs results into the
    # tables of a Relational Database.

    # Currently no batching is done. I.e. every match is writing every spectra one a at a time,
    # with individual round trips to the DB. Might have to update to include some form of batch
    # update.
    """

    def __init__(self, hostname, port, username, password, database, user_id):
        """
        Initialises the database connection and the writer in general.

        :param hostname: address of the database server
        :param username: database username/role to use for the connection
        :param password: password of the user/role
        :param port: port the database server is listening to
        :param database: name of the DB to write the result out to
        :param user_id: UUID of the UserAccount
        """
        # # Currently only MS2 Spectra are delt with
        # self.default_ms_level = 2

        # Connection setup.
        # The 'engine' in SQLAlchemy is a Factory and connection pool to the database.
        # It has lazy initialisation.
        self.engine = create_engine(
            f"postgresql://{username}:{password}@{hostname}:{port}/{database}"
        )
        self.meta = MetaData()
        self.upload_id = uuid4()
        self.user_id = user_id

        # with self.engine.connect() as conn:
        #
        #     # make sure we have the needed matched spectrum types in the DB
        #     self._init_matched_spectrum_types(conn)
        #
        #     self._init_result_set_types(conn)
        #
        #     self._prepare_search_tables(conn, self.search_uuid,
        #                                 self.result_set_uuid, self.json_config)
        #
        #     # Write the Proteins table from the context
        #     self._write_protein(conn, self.search_uuid, self.context.proteins)
        #
        #     self._write_score_names(conn, self.result_set_uuid)

    def new_upload(self, id_file_name):
        """
        Write a new Upload into the Database.

        ToDo: use write_data()?
        :param: id_file_name: file name of the identification file (mzid, csv)
        """
        upload = Table("Upload", self.meta, autoload_with=self.engine, quote=False)
        with self.engine.connect() as conn:
            stmt = insert(upload).values(
                id=str(self.upload_id),
                user_id=str(self.user_id),
                identification_filename=id_file_name,
            )
            conn.execute(stmt)

    def write_data(self, table, data):
        """
        Insert data into table.

        :param table: (str) Table name
        :param data: (list dict) data to insert.
        """
        table = Table(table, self.meta, autoload_with=self.engine, quote=False)
        with self.engine.connect() as conn:
            statement = table.insert().values(data)
            conn.execute(statement)
            conn.close()

    def write_mzid_info(self, peak_list_file_names, spectra_formats, analysis_software,
                        provider, audits, samples, analyses, protocol, bib):
        """
        Update Upload row with mzid info.

        ToDo: have this explicitly or create update func?
        :param peak_list_file_names:
        :param spectra_formats:
        :param analysis_software:
        :param provider:
        :param audits:
        :param samples:
        :param analyses:
        :param protocol:
        :param bib:
        :return:
        """
        upload = Table("Upload", self.meta, autoload_with=self.engine, quote=False)
        with self.engine.connect() as conn:
            stmt = upload.update().where(upload.c.id == str(self.upload_id)).values(
                peak_list_file_names=peak_list_file_names,
                spectra_formats=spectra_formats,
                analysis_software=analysis_software,
                provider=provider,
                audits=audits,
                samples=samples,
                analyses=analyses,
                protocol=protocol,
                bib=bib 
            )
            conn.execute(stmt)

    def write_other_info(self, contains_crosslinks, ident_count, ident_file_size,
                         upload_warnings):
        """
        Update Upload row with remaining info.

        ToDo: have this explicitly or create update func?
        :param contains_crosslinks:
        :param ident_count:
        :param ident_file_size:
        :param upload_warnings:
        :return:
        """
        upload = Table("Upload", self.meta, autoload_with=self.engine, quote=False)
        with self.engine.connect() as conn:
            stmt = upload.update().where(upload.c.id == str(self.upload_id)).values(
                contains_crosslinks=contains_crosslinks,
                upload_warnings=upload_warnings,
                ident_count=ident_count,
                ident_file_size=ident_file_size,
            )
            conn.execute(stmt)

    #
    # def write_db_sequences(self, inj_list):
    #     """
    #     Write the DBSequences.
    #
    #     :param inj_list: (list) data to write
    #     :return:
    #     """
    #     db_sequence = Table("DBSequence", self.meta, autoload_with=self.engine, quote=False)
    #     # # add the upload_id to all rows
    #     # inj_list = [x.update({'upload_id': self.upload_id}) for x in inj_list]
    #     with self.engine.connect() as conn:
    #         statement = db_sequence.insert().values(inj_list)
    #         conn.execute(statement, inj_list)
    #         conn.close()
    #         # {
    #         #     'id': bindparam('id'),
    #         #     'accession': bindparam('temperature'),
    #         #     'protein_name': bindparam('protein_name'),
    #         #     'description': bindparam('protein_name'),
    #         #     'sequence': bindparam('protein_name'),
    #         #     'upload_id': bindparam('upload_id'),
    #         #
    #         # }
    #
    # def write_peptides(self, inj_list):
    #     """
    #     Write the peptides.
    #
    #     :param inj_list: (list) data to write
    #     :return:
    #     """
    #     peptide = Table("Peptide", self.meta, autoload_with=self.engine, quote=False)
    #     with self.engine.connect() as conn:
    #         statement = peptide.insert().values(inj_list)
    #         conn.execute(statement, inj_list)
    #         conn.close()
    #     # cur.executemany("""
    #     # INSERT INTO peptides (
    #     #     id,
    #     #     seq_mods,
    #     #     link_site,
    #     #     crosslinker_modmass,
    #     #     upload_id,
    #     #     crosslinker_pair_id
    #     # )
    #     # VALUES (%s, %s, %s, %s, %s, %s)""", inj_list)
    #     # con.commit()