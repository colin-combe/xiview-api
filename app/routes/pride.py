from fastapi import APIRouter, Depends
from sqlalchemy import text
from typing import List

from app.models.projectdetail import ProjectDetail
from app.models.projectsubdetail import ProjectSubDetail
from index import get_session
from process_dataset import convert_pxd_accession_from_pride
from sqlalchemy.orm import Session, joinedload
import os
import requests
import logging.config

logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

pride_router = APIRouter()


@pride_router.post("/parse/{px_accession}", tags=["Main"])
async def parse(px_accession: str, temp_dir: str | None = None, dont_delete: bool = False):
    """
    Parse a new project which contain MzIdentML file
    :param px_accession: ProteomXchange Project Accession
    :param temp_dir: If data needs to be saved in a temporary directory
    :param dont_delete: Boolean value to determine if the files needs to be deleted at the end
    :return: None
    """
    if temp_dir:
        temp_dir = os.path.expanduser(temp_dir)
    else:
        temp_dir = os.path.expanduser('~/mzId_convertor_temp')
    convert_pxd_accession_from_pride(px_accession, temp_dir, dont_delete)


@pride_router.get("/projects", tags=["Main"])
async def list_all_projects(session: Session = Depends(get_session)) -> list[ProjectDetail]:
    """
    This gives the high-level view of list of projects
    :param session: connection to database
    :return: List of ProjectDetails in JSON format
    """
    projects = session.query(ProjectDetail).all()
    session.close()
    return projects


@pride_router.get("/projects/{px_accession}", tags=["Main"])
async def project_detail_view(px_accession, session: Session = Depends(get_session)) -> list[ProjectDetail]:
    project_details = session.query(ProjectDetail)\
        .options(joinedload(ProjectDetail.project_sub_details))\
        .filter(ProjectDetail.project_id == px_accession)\
        .all()
    session.close()
    return project_details


@pride_router.get("/health", tags=["Main"])
async def health():
    """
    A quick simple endpoint to test the API is working
    :return: Response with OK
    """
    logger.info('Checking the health-test')
    return "OK"


@pride_router.post("/update-project-details", tags=["Maintenance"])
async def update_project_details(session: Session = Depends(get_session)):
    """
    An endpoint to update the project details including title, description, PubmedID,
    Number of proteins, peptides and spectra identifications
    :param session: session connection to the dataset
    :return: None
    """

    # Get project accession List
    sql_project_accession_list = text("""
    SELECT DISTINCT u.project_id FROM upload u
    """)

    # Get total number of identifications (not spectra) passing Threshold including decoy identification
    sql_number_of_identifications = text("""
                    SELECT count(*)
                    FROM spectrumidentification
                    WHERE upload_id IN (
                        SELECT u.id
                        FROM upload u
                        WHERE u.upload_time = (
                            SELECT max(upload_time)
                            FROM upload
                            WHERE project_id = u.project_id AND identification_file_name = u.identification_file_name
                        )
                        AND u.project_id = :projectaccession
                    )
                    AND pass_threshold = True
                """)

    # Get Total number of peptides identified passing Threshold including decoy identification(including non-crosslink)
    sql_number_of_peptides = text("""
                            SELECT COUNT(DISTINCT pep_id)
                            FROM (
                                SELECT pep1_id AS pep_id
                                FROM spectrumidentification si
                                WHERE si.upload_id IN (
                                        SELECT u.id
                                        FROM upload u
                                        where u.upload_time =
                                            (select max(upload_time) from upload
                                            where project_id = u.project_id
                                            and identification_file_name = u.identification_file_name )
                                            and u.project_id = :projectaccession
                                ) AND si.pass_threshold = TRUE

                                UNION

                                SELECT pep2_id AS pep_id
                                FROM spectrumidentification si
                                WHERE si.upload_id IN (
                                        SELECT u.id
                                        FROM upload u
                                        where u.upload_time =
                                            (select max(upload_time) from upload
                                            where project_id = u.project_id
                                            and identification_file_name = u.identification_file_name )
                                            and u.project_id = :projectaccession
                                ) AND si.pass_threshold = TRUE
                            ) AS result;    
        """)

    # Total number of crosslinked proteins identified passing Threshold excluding decoy identification
    sql_number_of_proteins = text("""
                        SELECT COUNT(*) 
                        FROM (
                            SELECT DISTINCT dbs.accession 
                            FROM (
                                SELECT pe1.dbsequence_ref AS protein_id
                                FROM spectrumidentification si
                                INNER JOIN modifiedpeptide mp1 ON si.pep1_id = mp1.id AND si.upload_id = mp1.upload_id
                                INNER JOIN peptideevidence pe1 ON mp1.id = pe1.peptide_ref AND mp1.upload_id = pe1.upload_id
                                INNER JOIN modifiedpeptide mp2 ON si.pep2_id = mp2.id AND si.upload_id = mp2.upload_id
                                INNER JOIN peptideevidence pe2 ON mp2.id = pe2.peptide_ref AND mp2.upload_id = pe2.upload_id
                                INNER JOIN upload u ON u.id = si.upload_id
                                WHERE u.id IN (
                                    SELECT u.id
                                    FROM upload u
                                    WHERE u.upload_time = (
                                        SELECT MAX(upload_time)
                                        FROM upload
                                        WHERE project_id = u.project_id
                                        AND identification_file_name = u.identification_file_name
                                    ) AND u.project_id = :projectaccession
                                ) AND mp1.link_site1 > 0 AND mp2.link_site1 > 0 AND pe1.is_decoy = FALSE AND pe2.is_decoy = FALSE
                                AND si.pass_threshold = TRUE

                                UNION

                                SELECT pe2.dbsequence_ref AS protein_id
                                FROM spectrumidentification si
                                INNER JOIN modifiedpeptide mp1 ON si.pep1_id = mp1.id AND si.upload_id = mp1.upload_id
                                INNER JOIN peptideevidence pe1 ON mp1.id = pe1.peptide_ref AND mp1.upload_id = pe1.upload_id
                                INNER JOIN modifiedpeptide mp2 ON si.pep2_id = mp2.id AND si.upload_id = mp2.upload_id
                                INNER JOIN peptideevidence pe2 ON mp2.id = pe2.peptide_ref AND mp2.upload_id = pe2.upload_id
                                INNER JOIN upload u ON u.id = si.upload_id
                                WHERE u.id IN (
                                    SELECT u.id
                                    FROM upload u
                                    WHERE u.upload_time = (
                                        SELECT MAX(upload_time)
                                        FROM upload
                                        WHERE project_id = u.project_id
                                        AND identification_file_name = u.identification_file_name
                                    ) AND u.project_id = :projectaccession
                                ) AND mp1.link_site1 > 0 AND mp2.link_site1 > 0 AND pe1.is_decoy = FALSE AND pe2.is_decoy = FALSE
                                AND si.pass_threshold = TRUE
                            ) AS protein_id 
                            INNER JOIN dbsequence AS dbs ON protein_id = id
                        ) AS accessions;

        """)

    # total number of peptides(crosslink and non crosslink) per protein
    sql_peptides_per_protein = text("""
    WITH result AS (
    SELECT
        pe1.dbsequence_ref AS dbref1,
        pe1.peptide_ref AS pepref1,
        pe2.dbsequence_ref AS dbref2,
        pe2.peptide_ref AS pepref2
    FROM
        spectrumidentification si
        INNER JOIN modifiedpeptide mp1 ON si.pep1_id = mp1.id AND si.upload_id = mp1.upload_id
        INNER JOIN peptideevidence pe1 ON mp1.id = pe1.peptide_ref AND mp1.upload_id = pe1.upload_id
        INNER JOIN modifiedpeptide mp2 ON si.pep2_id = mp2.id AND si.upload_id = mp2.upload_id
        INNER JOIN peptideevidence pe2 ON mp2.id = pe2.peptide_ref AND mp2.upload_id = pe2.upload_id
        INNER JOIN upload u ON u.id = si.upload_id
    WHERE
        u.id IN (
            SELECT u.id
            FROM upload u
            WHERE u.upload_time = (
                SELECT MAX(upload_time)
                FROM upload
                WHERE project_id = u.project_id
                AND identification_file_name = u.identification_file_name
            ) AND u.project_id = :projectaccession
        )
        AND pe1.is_decoy = FALSE
        AND pe2.is_decoy = FALSE
        AND si.pass_threshold = TRUE
)
SELECT
    dbref,
    COUNT(pepref) AS peptide_count
FROM (
    SELECT dbref1 AS dbref, pepref1 AS pepref FROM result
    UNION
    SELECT dbref2 AS dbref, pepref2 AS pepref FROM result
) AS inner_result
GROUP BY dbref;

    """)

    # Proteins and crosslink peptide counts
    sql_crosslinks_per_protein = text("""
 WITH result AS (
    SELECT
        pe1.dbsequence_ref AS dbref1,
        pe1.peptide_ref AS pepref1,
        pe2.dbsequence_ref AS dbref2,
        pe2.peptide_ref AS pepref2
    FROM
        spectrumidentification si
        INNER JOIN modifiedpeptide mp1 ON si.pep1_id = mp1.id AND si.upload_id = mp1.upload_id
        INNER JOIN peptideevidence pe1 ON mp1.id = pe1.peptide_ref AND mp1.upload_id = pe1.upload_id
        INNER JOIN modifiedpeptide mp2 ON si.pep2_id = mp2.id AND si.upload_id = mp2.upload_id
        INNER JOIN peptideevidence pe2 ON mp2.id = pe2.peptide_ref AND mp2.upload_id = pe2.upload_id
        INNER JOIN upload u ON u.id = si.upload_id
    WHERE
        u.id IN (
            SELECT u.id
            FROM upload u
            WHERE u.upload_time = (
                SELECT MAX(upload_time)
                FROM upload
                WHERE project_id = u.project_id
                AND identification_file_name = u.identification_file_name
            ) AND u.project_id = :projectaccession
        )
        AND mp1.link_site1 > 0
        AND mp2.link_site1 > 0
        AND pe1.is_decoy = FALSE
        AND pe2.is_decoy = FALSE
        AND si.pass_threshold = TRUE
)
SELECT
    dbref,
    COUNT(pepref) AS peptide_count
FROM (
    SELECT DISTINCT *
    FROM (
        SELECT dbref1 AS dbref, pepref1 AS pepref FROM result
        UNION
        SELECT dbref2 AS dbref, pepref2 AS pepref FROM result
    ) AS inner_inner_result
) AS inner_result
GROUP BY dbref;

       """)

    # Protein dbref to protein accession mapping
    sql_db_sequence_accession_mapping = text("""
    SELECT id, accession
    FROM dbsequence
    WHERE upload_id IN (
        SELECT u.id
        FROM upload u
        WHERE u.upload_time = (
            SELECT MAX(upload_time)
            FROM upload
            WHERE project_id = u.project_id
            AND identification_file_name = u.identification_file_name
        )
        AND u.project_id = :projectaccession
    );
    """)

#     # number of peptides of a selected protein
#     sql_number_of_peptides_of_selected_protein = text("""
# SELECT COUNT(pe.peptide_ref)
# FROM peptideevidence pe
# WHERE
#     pe.dbsequence_ref IN (
#         SELECT id
#         FROM dbsequence
#         WHERE
#             accession = :proteinaccession
#             AND upload_id IN (
#                 SELECT u.id
#                 FROM upload u
#                 WHERE
#                     u.upload_time = (
#                         SELECT MAX(upload_time)
#                         FROM upload
#                         WHERE
#                             project_id = u.project_id
#                             AND identification_file_name = u.identification_file_name
#                     )
#                     AND u.project_id = :projectaccession
#             )
#     )
#     AND pe.is_decoy = FALSE;
#     """)
#
#     # number of crosslinks of a selected protein
#     sql_number_of_crosslinks_of_selected_protein = text("""
#     SELECT DISTINCT crosslinker_pair_id
# FROM modifiedpeptide mp
# WHERE
#     mp.upload_id IN (
#         SELECT u.id
#         FROM upload u
#         WHERE
#             u.upload_time = (
#                 SELECT MAX(upload_time)
#                 FROM upload
#                 WHERE
#                     project_id = u.project_id
#                     AND identification_file_name = u.identification_file_name
#             )
#             AND u.project_id = :projectaccession
#     )
#     AND mp.id IN (
#         SELECT pe.peptide_ref
#         FROM peptideevidence pe
#         WHERE
#             pe.dbsequence_ref IN (
#                 SELECT id
#                 FROM dbsequence
#                 WHERE
#                     accession = :proteinaccession
#                     AND upload_id IN (
#                         SELECT u.id
#                         FROM upload u
#                         WHERE
#                             u.upload_time = (
#                                 SELECT MAX(upload_time)
#                                 FROM upload
#                                 WHERE
#                                     project_id = u.project_id
#                                     AND identification_file_name = u.identification_file_name
#                             )
#                             AND u.project_id = :projectaccession
#                     )
#             )
#             AND pe.is_decoy = FALSE
#     );
#
#     """)

    try:
        sql_values = {}
        list_of_accessions = await get_accessions(sql_project_accession_list, sql_values, session)
        for accession in list_of_accessions:
            project_details = ProjectDetail()
            sql_values = {"projectaccession": accession}

            # get project details from PRIDE API
            # TODO: need to move URL to a configuration variable
            px_url = 'https://www.ebi.ac.uk/pride/ws/archive/v2/projects/' + accession
            logger.debug('GET request to PRIDE API: ' + px_url)
            pride_response = requests.get(px_url)
            r = requests.get(px_url)
            if r.status_code == 200:
                print('PRIDE API returned status code 200')
                pride_json = pride_response.json()
                if len(pride_json['references']) > 0:
                    pubmedId = pride_json['references'][0]['pubmedId']
                    project_details.pubmed_id = pubmedId
                if pride_json is not None:
                    project_details.title = pride_json['title']
                    project_details.description = pride_json['projectDescription']
            project_details.project_id = accession

            project_details.number_of_spectra = await get_number_of_counts(sql_number_of_identifications, sql_values, session)
            project_details.number_of_peptides = await get_number_of_counts(sql_number_of_peptides, sql_values, session)
            project_details.number_of_proteins = await get_number_of_counts(sql_number_of_proteins, sql_values, session)

            peptide_counts_by_protein = await get_counts_table(sql_peptides_per_protein, sql_values, session)
            peptide_crosslinks_by_protein = await get_counts_table(sql_crosslinks_per_protein, sql_values, session)
            db_sequence_accession_mapping = await get_counts_table(sql_db_sequence_accession_mapping, sql_values, session)

            list_of_project_sub_details = []

            # fill number of peptides
            for protein in peptide_counts_by_protein:
                project_sub_detail = ProjectSubDetail()
                project_sub_detail.protein_db_ref = protein['key']
                project_sub_detail.number_of_peptides = protein['value']
                list_of_project_sub_details.append(project_sub_detail)

            # fill number of crosslink
            for crosslinks in peptide_crosslinks_by_protein:
                for sub_details in list_of_project_sub_details:
                    if sub_details.protein_db_ref == crosslinks['key']:
                        sub_details.number_of_cross_links = crosslinks['value']

            # fill protein accessions
            for sub_details in list_of_project_sub_details:
                for dbseq in db_sequence_accession_mapping:
                    if sub_details.protein_db_ref == dbseq['key']:
                        sub_details.protein_accession = dbseq['value']

            project_details.project_sub_details = list_of_project_sub_details
            logger.info(project_details.__dict__)

            # Define the conditions for updating
            conditions = {'project_id': accession}

            # Query for an existing record based on conditions
            existing_record = session.query(ProjectDetail).filter_by(**conditions).first()

            # If the record exists, update its attributes
            if existing_record:
                existing_record.title = project_details.title
                existing_record.description = project_details.description
                existing_record.pubmed_id = project_details.pubmed_id
                existing_record.number_of_proteins = project_details.number_of_proteins
                existing_record.number_of_peptides = project_details.number_of_peptides
                existing_record.number_of_spectra = project_details.number_of_spectra
                existing_record.project_sub_details = list_of_project_sub_details
            else:
                session.add(project_details)
            session.commit()
            session.close()
    except Exception as error:
        logger.error(error)


async def get_number_of_counts(sql, sql_values, session):
    """
    Get total number of counts (protein, peptide, spectra Identification) for a given project
    :param sql: sql statements for counts
    :param sql_values: Values for SQl(i.e Project accession or protein accession)
    :param session: database session
    :return: total number of counts
    """
    number_of_counts = 0
    try:
        result = session.execute(sql, sql_values)
        number_of_counts = result.scalar()
    except Exception as error:
        logger.error(error)
    finally:
        session.close()
        logger.debug('Database session is closed.')
    return number_of_counts


async def get_accessions(sql, sql_values, session):
    """
    Get all the Unique accessions(project, protein) in the database according to the SQL
    :param sql_values: SQl Values
    :param sql: SQL to get project accessions
    :param session: database session
    :return: List of unique project accessions
    """
    try:
        result = session.execute(sql, sql_values)
        # Fetch the list of accessions
        list_of_accessions = [row[0] for row in result]
    except Exception as error:
        logger.error(error)
    finally:
        session.close()
        logger.debug('Database session is closed.')
    return list_of_accessions


async def get_counts_table(sql, sql_values, session):
    """
    Get table of data in the database according to the SQL
    :param sql_values: SQl Values
    :param sql: SQL to get project accessions
    :param session: database session
    :return: List of key value pairs
    """
    try:
        result = session.execute(sql, sql_values)
        result_list = [
            {'key': row[0], 'value': row[1]} for row in result if len(row) >= 2
        ]
    except Exception as error:
        logger.error(error)
    finally:
        session.close()
        logger.debug('Database session is closed.')
    return result_list