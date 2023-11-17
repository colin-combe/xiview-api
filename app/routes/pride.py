from fastapi import APIRouter, Depends
from sqlalchemy import text
from app.models.projectdetails import ProjectDetails
from index import get_session
from process_dataset import convert_pxd_accession_from_pride
from sqlalchemy.orm import Session
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
async def list_all_projects(session: Session = Depends(get_session)) -> list[ProjectDetails]:
    """
    This gives the high-level view of list of projects
    :param session: connection to database
    :return: List of ProjectDetails in JSON format
    """
    projects = session.query(ProjectDetails).all()
    session.close()
    return projects


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
                                    ) AND u.project_id = 'PXD036833'
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
                                    ) AND u.project_id = 'PXD036833'
                                ) AND mp1.link_site1 > 0 AND mp2.link_site1 > 0 AND pe1.is_decoy = FALSE AND pe2.is_decoy = FALSE
                                AND si.pass_threshold = TRUE
                            ) AS protein_id 
                            INNER JOIN dbsequence AS dbs ON protein_id = id
                        ) AS accessions;

        """)

    try:
        list_of_accessions = await get_project_accessions(session)
        for accession in list_of_accessions:
            projectDetails = ProjectDetails()

            # get project details from PRIDE API
            # TODO: need to move URL to a configuration variable
            px_url = 'https://www.ebi.ac.uk/pride/ws/archive/v2/projects/' + accession
            logger.debug('GET request to PRIDE API: ' + px_url)
            pride_response = requests.get(px_url)
            r = requests.get(px_url)
            if r.status_code == 200:
                print('PRIDE API returned status code 200')
                pride_json = pride_response.json()
                pubmedId = ''
                if len(pride_json['references']) > 0:
                    pubmedId = pride_json['references'][0]['pubmedId']
                    projectDetails.pubmed_id = pubmedId
                if pride_json is not None:
                    projectDetails.title = pride_json['title']
                    projectDetails.description = pride_json['projectDescription']
            projectDetails.project_id = accession

            projectDetails.number_of_spectra = await get_number_of_counts(sql_number_of_identifications, accession,
                                                                          session)
            logger.info("Total number of spectra for " + accession + " is: " + str(projectDetails.number_of_spectra))
            projectDetails.number_of_peptides = await get_number_of_counts(sql_number_of_peptides, accession, session)
            logger.info("Total number of peptide for " + accession + " is: " + str(projectDetails.number_of_peptides))
            projectDetails.number_of_proteins = await get_number_of_counts(sql_number_of_proteins, accession, session)
            logger.info("Total number of protein for " + accession + " is: " + str(projectDetails.number_of_proteins))

            logger.info(projectDetails.__dict__)

            # Define the conditions for updating
            conditions = {'project_id': accession}

            # Query for an existing record based on conditions
            existing_record = session.query(ProjectDetails).filter_by(**conditions).first()

            # If the record exists, update its attributes
            if existing_record:
                existing_record.title = projectDetails.title
                existing_record.description = projectDetails.description
                existing_record.pubmed_id = projectDetails.pubmed_id
                existing_record.number_of_proteins = projectDetails.number_of_proteins
                existing_record.number_of_peptides = projectDetails.number_of_peptides
                existing_record.number_of_spectra = projectDetails.number_of_spectra
            else:
                session.add(projectDetails)
            session.commit()
            session.close()
    except Exception as error:
        logger.error(error)


async def get_number_of_counts(sql, accession, session):
    """
    Get total number of counts (protein, peptide, spectra Identification) for a given project
    :param sql: sql statements for counts
    :param accession: Project accession
    :param session: database session
    :return: total number of counts
    """
    number_of_counts = 0
    try:
        result = session.execute(sql, {"projectaccession": accession})
        number_of_counts = result.scalar()
    except Exception as error:
        logger.error(error)
    finally:
        session.close()
        logger.debug('Database session is closed.')
    return number_of_counts


async def get_project_accessions(session):
    """
    Get all the Unique project accessions in the database Upload table
    :param session: database session
    :return: List of unique project accessions
    """

    sql = text("SELECT DISTINCT u.project_id FROM upload u")
    try:
        result = session.execute(sql)
        # Fetch the list of accessions
        list_of_accessions = [row[0] for row in result]
    except Exception as error:
        logger.error(error)
    finally:
        session.close()
        logger.debug('Database session is closed.')
    return list_of_accessions