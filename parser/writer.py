from uuid import uuid4
from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table as SATable
from sqlalchemy.dialects.postgresql import insert


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
                identification_file_name=id_file_name,
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

    def write_mzid_info(self, spectra_formats,
                        provider, audits, samples, bib):
        """
        Update Upload row with mzid info.

        ToDo: have this explicitly or create update func?
        :param spectra_formats:
        :param provider:
        :param audits:
        :param samples:
        :param bib:
        :return:
        """
        upload = Table("Upload", self.meta, autoload_with=self.engine, quote=False)
        stmt = upload.update().where(upload.c.id == str(self.upload_id)).values(
            spectra_formats=spectra_formats,
            provider=provider,
            audits=audits,
            samples=samples,
            bib=bib
        )
        with self.engine.connect() as conn:
            conn.execute(stmt)

    def write_other_info(self, contains_crosslinks, ident_file_size, upload_warnings):
        """
        Update Upload row with remaining info.

        ToDo: have this explicitly or create update func?
        :param contains_crosslinks:
        :param ident_file_size:
        :param upload_warnings:
        :return:
        """
        upload = Table("Upload", self.meta, autoload_with=self.engine, quote=False)
        with self.engine.connect() as conn:
            stmt = upload.update().where(upload.c.id == str(self.upload_id)).values(
                contains_crosslinks=contains_crosslinks,
                upload_warnings=upload_warnings,
                ident_file_size=ident_file_size,
            )
            conn.execute(stmt)