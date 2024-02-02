import configparser
import os
from operator import and_
from typing import List
import sys

import requests
from fastapi import APIRouter, Depends, status, Query
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy import text, select, or_
from sqlalchemy.orm import Session, joinedload
from app.models.upload import Upload
from app.models.analysiscollection import AnalysisCollection
from app.models.dbsequence import DBSequence
from app.models.enzyme import Enzyme
from app.models.modifiedpeptide import ModifiedPeptide
from app.models.peptideevidence import PeptideEvidence
from app.models.projectdetail import ProjectDetail
from app.models.projectsubdetail import ProjectSubDetail
from app.models.searchmodification import SearchModification
from app.models.spectrum import Spectrum
from app.models.spectrumidentification import SpectrumIdentification
from app.models.spectrumidentificationprotocol import SpectrumIdentificationProtocol
from app.routes.shared import get_api_key
from index import get_session
from process_dataset import convert_pxd_accession_from_pride

import logging
import logging.config

logger = logging.getLogger(__name__)
pride_router = APIRouter()
config = configparser.ConfigParser()


@pride_router.get("/health", tags=["Admin"])
async def health(session: Session = Depends(get_session)):
    """
    A quick simple endpoint to test the API is working
    :return: Response with OK
    """

    sql_projects_count = text("""
                          SELECT
                              COUNT(id) AS "Number of Projects"
                          FROM
                              projectdetails p;
                      """)
    try:
        count = await get_projects_count(sql_projects_count, session)
        if count[0] is not None:
            db_status = "OK"
        else:
            db_status = "Failed"
    except Exception as error:
        logger.error(error)
        db_status = "Failed"
    logger.info('Health check endpoint accessed')
    logger.debug('Health check endpoint accessed - debug')
    return {'status': "OK",
            'db_status': db_status}


@pride_router.post("/parse", tags=["Admin"])
async def parse(px_accession: str, temp_dir: str | None = None, dont_delete: bool = False,
                api_key: str = Security(get_api_key)):
    """
    Parse a new project which contain MzIdentML file
    :param api_key: API KEY
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


@pride_router.post("/update-protein-metadata/{project_id}", tags=["Admin"])
async def update_metadata_by_project(project_id: str, session: Session = Depends(get_session),
                                     api_key: str = Security(get_api_key)):
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

    project_details = ProjectDetail()
    sql_values = {"projectaccession": project_id}

    # get project details from PRIDE API
    logger.info("Updating project level metadata")
    px_url = 'https://www.ebi.ac.uk/pride/ws/archive/v2/projects/' + project_id
    logger.debug('GET request to PRIDE API: ' + px_url)
    pride_response = requests.get(px_url)
    r = requests.get(px_url)
    if r.status_code == 200:
        logger.info('PRIDE API returned status code 200')
        pride_json = pride_response.json()
        if pride_json is not None:
            if len(pride_json['references']) > 0:
                project_details.pubmed_id = pride_json['references'][0]['pubmedId']
            if len(pride_json['title']) > 0:
                project_details.title = pride_json['title']
            if len(pride_json['projectDescription']) > 0:
                project_details.description = pride_json['projectDescription']
            if len(pride_json['organisms']) > 0:
                project_details.organism = pride_json['organisms'][0]['name']

    project_details.project_id = project_id

    project_details.number_of_spectra = await get_number_of_counts(sql_number_of_identifications, sql_values,
                                                                   session)
    project_details.number_of_peptides = await get_number_of_counts(sql_number_of_peptides, sql_values, session)
    project_details.number_of_proteins = await get_number_of_counts(sql_number_of_proteins, sql_values, session)

    peptide_counts_by_protein = await get_counts_table(sql_peptides_per_protein, sql_values, session)
    peptide_crosslinks_by_protein = await get_counts_table(sql_crosslinks_per_protein, sql_values, session)
    db_sequence_accession_mapping = await get_counts_table(sql_db_sequence_accession_mapping, sql_values,
                                                           session)

    list_of_project_sub_details = []

    # fill number of peptides
    for protein in peptide_counts_by_protein:
        project_sub_detail = ProjectSubDetail()
        project_sub_detail.project_detail = project_details
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

    logger.info("Updating protein level metadata")
    await update_protein_metadata(list_of_project_sub_details)

    logger.info("Saving medatadata...")
    conditions = {'project_id': project_id}
    existing_record = session.query(ProjectDetail).filter_by(**conditions).first()

    # If the record exists, update its attributes
    if existing_record:
        # Delete ProjectDetail and associated ProjectSubDetail records based on project_detail_id
        session.query(ProjectSubDetail).filter_by(project_detail_id=existing_record.id).delete()
        session.query(ProjectDetail).filter_by(**conditions).delete()
        session.commit()

    # add new record
    session.add(project_details)
    session.commit()
    logger.info("Saving medatadata COMPLETED")
    return 0


@pride_router.post("/update-metadata", tags=["Admin"])
async def update_metadata(session: Session = Depends(get_session), api_key: str = Security(get_api_key)):
    """
    An endpoint to update the project details including title, description, PubmedID,
    Number of proteins, peptides and spectra identifications
    :param api_key: API KEY
    :param session: session connection to the database
    :return: None
    """

    sql_project_accession_list = text("""
    SELECT DISTINCT u.project_id FROM upload u
    """)

    try:
        sql_values = {}
        list_of_project_id = await get_accessions(sql_project_accession_list, sql_values, session)
        for project_id in list_of_project_id:
            await update_metadata_by_project(project_id, session, api_key)
        session.close()
    except Exception as error:
        logger.error(error)
        session.rollback()


@pride_router.put("/log/{level}", tags=["Admin"])
def change_log_level(level, api_key: str = Security(get_api_key)):
    level_upper = str(level).upper()
    logging.getLogger("uvicorn.error").setLevel(level_upper)
    logging.getLogger("uvicorn.access").setLevel(level_upper)
    logging.getLogger("uvicorn.asgi").setLevel(level_upper)
    logger.setLevel(level_upper)


@pride_router.delete("/delete/{project_id}", tags=["Admin"])
async def delete_dataset(project_id: str, session: Session = Depends(get_session),
                         api_key: str = Security(get_api_key)):
    logger.info("Deleting dataset: " + project_id)

    try:
        # Define the conditions for updating
        conditions = {'project_id': project_id}

        # Query for an existing record based on conditions
        existing_upload_record = session.query(Upload).filter_by(**conditions).first()

        # If the record exists, update its attributes
        if existing_upload_record:
            # Delete ProjectDetail and associated ProjectSubDetail records based on project_detail_id
            session.query(ProjectSubDetail).filter_by(project_detail_id=existing_upload_record.id).delete()
            session.query(ProjectDetail).filter_by(project_id=project_id).delete()
            session.query(SpectrumIdentification).filter_by(upload_id=existing_upload_record.id).delete()
            session.query(SearchModification).filter_by(upload_id=existing_upload_record.id).delete()
            session.query(Enzyme).filter_by(upload_id=existing_upload_record.id).delete()
            session.query(SpectrumIdentificationProtocol).filter_by(upload_id=existing_upload_record.id).delete()
            session.query(ModifiedPeptide).filter_by(upload_id=existing_upload_record.id).delete()
            session.query(DBSequence).filter_by(upload_id=existing_upload_record.id).delete()
            session.query(Spectrum).filter_by(upload_id=existing_upload_record.id).delete()
            session.query(PeptideEvidence).filter_by(upload_id=existing_upload_record.id).delete()
            session.query(AnalysisCollection).filter_by(upload_id=existing_upload_record.id).delete()
            session.query(Upload).filter_by(**conditions).delete()
            session.commit()
    except Exception as error:
        logger.error(str(error))
        session.rollback()
    finally:
        # This is the same as the `get_db` method below
        session.close()


@pride_router.get("/projects", tags=["Projects"])
async def list_all_projects(session: Session = Depends(get_session), page: int = 1, page_size: int = 10) -> list[
    ProjectDetail]:
    """
    This gives the high-level view of list of projects
    :param session: connection to database
    :param page: page number
    :param page_size: number of records per page
    :return: List of ProjectDetails in JSON format
    """
    try:
        offset = (page - 1) * page_size
        projects = session.query(ProjectDetail).offset(offset).limit(page_size).all()
    except Exception as e:
        # Handle the exception here
        logging.error(f"Error occurred: {str(e)}")
        return []
    if projects is None or projects == []:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projects not found")

    return projects

@pride_router.get("/projects/search", tags=["Projects"])
async def project_search(query: str = Query(...),
                            page: int = 1,
                            page_size: int = 10,
                            session: Session = Depends(get_session)
                            ) -> list[ProjectDetail]:
    """
    This gives the high-level view of list of projects
    :param session: connection to database
    :param page: page number
    :param page_size: number of records per page
    :return: List of ProjectDetails in JSON format
    """
    project_search_sql = text("""
        SELECT p.id FROM projectdetails p
    JOIN public.projectsubdetails ps ON p.id = ps.project_detail_id
    WHERE p.project_id = :query OR
          p.title ILIKE '%' || :query || '%' OR
          p.description ILIKE '%' || :query || '%' OR
          p.organism ILIKE '%' || :query || '%' OR
          ps.protein_accession = :query OR
          ps.protein_name ILIKE '%' || :query || '%' OR
          ps.gene_name ILIKE '%' || :query || '%'
      """)
    matchig_ids = session.execute(project_search_sql, {"query": query}).fetchall()
    list_of_ids = [id for (id,) in matchig_ids]

    try:
            offset = (page - 1) * page_size
            projects = session.query(ProjectDetail).filter(ProjectDetail.id.in_(list_of_ids)).offset(offset).limit(page_size).all()
    except Exception as e:
            # Handle the exception here
            logging.error(f"Error occurred: {str(e)}")
            return []
    if projects is None or projects == []:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projects not found")

    return projects



@pride_router.get("/projects/{project_id}/proteins", tags=["Projects"])
async def protein_search(   project_id: str,
                            query: str | None = None,
                            page: int = 1,
                            page_size: int = 10,
                            session: Session = Depends(get_session)
                            ) -> list[ProjectSubDetail]:
    """
    This gives the high-level view of a list of projects
    :param session: connection to the database
    :param page: page number
    :param page_size: number of records per page
    :return: List of ProjectDetails in JSON format
    """
    try:
        if query is None or query =='*':
            sql = text("""
                                  SELECT * FROM projectsubdetails 
                                  WHERE project_detail_id IN (SELECT id 
                                                              FROM projectdetails 
                                                              WHERE project_id = :project_id)
                                  ORDER BY id
                                  LIMIT :limit OFFSET :offset
                              """)
            sql_values = {
                "project_id": project_id,
                "limit": page_size,
                "offset": (page - 1) * page_size
            }
        else:
            sql = text("""
                                  SELECT * FROM projectsubdetails 
                                  WHERE (protein_accession LIKE '%' || :query || '%' OR
                                         gene_name LIKE '%' || :query || '%' OR
                                         protein_name LIKE '%' || :query || '%') 
                                         AND project_detail_id IN (SELECT id 
                                                                   FROM projectdetails 
                                                                   WHERE project_id = :project_id)
                                  ORDER BY id
                                  LIMIT :limit OFFSET :offset
                              """)
            sql_values = {
                "project_id": project_id,
                "query": query,
                "limit": page_size,
                "offset": (page - 1) * page_size
            }

        result = session.execute(sql, sql_values)
        proteins = result.fetchall()

        # Convert rows to a list of ProjectSubDetail objects
        proteins_list = []
        for row in proteins:
            protein = ProjectSubDetail(
                id = row.id,
                project_detail_id = row.project_detail_id,
                protein_db_ref = row.protein_db_ref,
                protein_name = row.protein_name,
                gene_name = row.gene_name,
                protein_accession = row.protein_accession,
                number_of_peptides = row.number_of_peptides,
                number_of_cross_links = row.number_of_cross_links,
                in_pdbe_kb = row.in_pdbe_kb,
                in_alpha_fold_db = row.in_alpha_fold_db
            )
            proteins_list.append(protein)

    except Exception as e:
        # Handle the exception here
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

    if not proteins_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="proteins not found")

    return proteins_list

@pride_router.get("/projects/{project_id}", tags=["Projects"])
def project_detail_view(project_id: str, session: Session = Depends(get_session)) -> List[ProjectDetail]:
    """
    Retrieve project detail by px_accession.
    :param project_id: identifier of a project, for ProteomeXchange projects this is the PXD****** accession
    :param session:
    :return:
    """
    try:
        project_detail = session.query(ProjectDetail) \
            .options(joinedload(ProjectDetail.project_sub_details)) \
            .filter(ProjectDetail.project_id == project_id) \
            .all()
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        project_detail = None

    if project_detail is None or project_detail == []:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project detail not found")

    return project_detail


@pride_router.get("/projects/{project_id}/proteins", tags=["Projects"])
def project_detail_view(project_id: str, session: Session = Depends(get_session), page: int = 1, page_size: int = 10) -> \
        list[ProjectSubDetail]:
    """
    Retrieve protein detail by px_accession.
    """
    try:
        project_detail = session.query(ProjectDetail) \
            .options(joinedload(ProjectDetail.project_sub_details)) \
            .filter(ProjectDetail.project_id == project_id).scalar()

        offset = (page - 1) * page_size
        project_sub_details = session.query(ProjectSubDetail).filter(
            ProjectSubDetail.project_detail_id == project_detail.id) \
            .offset(offset).limit(page_size).all()

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        project_sub_details = None

    if project_sub_details is None or project_sub_details == []:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project detail not found")

    return project_sub_details


@pride_router.get("/statistics-count", tags=["Statistics"])
async def statistics_count(session: Session = Depends(get_session)):
    try:
        sql_statistics_count = text("""
                      SELECT
                          COUNT(id) AS "Number of Projects",
                          SUM(number_of_proteins) AS "Number of proteins",
                          SUM(number_of_peptides) AS "Number of peptides",
                          SUM(number_of_spectra) AS "Number of spectra",
                          COUNT(DISTINCT organism) AS "Number of species"
                      FROM
                          projectdetails p;
                  """)
        values = await get_statistics_count(sql_statistics_count, session)
    except Exception as error:
        logger.error(error)
    return values


@pride_router.get("/projects-per-species", tags=["Statistics"])
async def project_per_species(session: Session = Depends(get_session)):
    """
    Number of projects per species
    :param session: session connection to the database
    :return:  Number of projects per species as a Dictionary
    """
    try:
        sql_projects_per_species = text("""
        SELECT organism, COUNT(organism) AS organism_count
        FROM projectdetails
        GROUP BY organism
        ORDER BY COUNT(organism) ASC;
""")
        values = await project_per_species_counts(sql_projects_per_species, None, session)
    except Exception as error:
        logger.error(error)
    return values


@pride_router.get("/peptide-per-protein", tags=["Statistics"])
async def peptide_per_protein(session: Session = Depends(get_session)):
    """
    Get the number of peptides per protein frequency
    :param session: session connection to the database
    :return:  Number of peptides per protein frequency as a dictionary
    """
    try:
        sql_peptides_per_protein = text("""
        WITH frequencytable AS (
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
                SELECT
                    u.id
                FROM
                    upload u
                WHERE
                    u.upload_time = (
                        SELECT
                            MAX(upload_time)
                        FROM
                            upload
                        WHERE
                            project_id = u.project_id
                            AND identification_file_name = u.identification_file_name
                    )
            )
            AND pe1.is_decoy = FALSE
            AND pe2.is_decoy = FALSE
            AND si.pass_threshold = TRUE
    )
    SELECT
        dbref,
        COUNT(pepref) AS peptide_count
    FROM
        (
            SELECT
                dbref1 AS dbref,
                pepref1 AS pepref
            FROM
                result
            UNION
            SELECT
                dbref2 AS dbref,
                pepref2 AS pepref
            FROM
                result
        ) AS inner_result
    GROUP BY
        dbref
)
SELECT
    frequencytable.peptide_count,
    COUNT(*)
FROM
    frequencytable
GROUP BY
    frequencytable.peptide_count
ORDER BY
    frequencytable.peptide_count;

""")
        values = await peptide_per_protein_counts(sql_peptides_per_protein, None, session)
    except Exception as error:
        logger.error(error)
    return values


async def update_protein_metadata(list_of_project_sub_details):
    # 1. metadata from Uniprot
    logger.info("Updating protein level metadata from Uniprot API...")
    uniprot_records = await find_uniprot_data(list_of_project_sub_details)
    list_of_project_sub_details = await extract_uniprot_data(list_of_project_sub_details, uniprot_records)
    logger.info("Updating protein level metadata from Uniprot API COMPLETED")

    # 2. metadata from PDBe
    logger.info("Updating protein level metadata from PDBe API...")
    base_in_URL = "https://www.ebi.ac.uk/pdbe/api/mappings/best_structures/"
    list_of_project_sub_details = await find_data_availability(list_of_project_sub_details, base_in_URL, "PDBe")
    logger.info("Updating protein level metadata from PDBe API COMPLETED")

    # 3. metadata from AlphaFold
    logger.info("Updating protein level metadata from AlphaFold API...")
    base_in_URL = "https://alphafold.ebi.ac.uk/api/prediction/"
    list_of_project_sub_details = await find_data_availability(list_of_project_sub_details, base_in_URL, "AlphaFold")
    logger.info("Updating protein level metadata from AlphaFold API COMPLETED")
    logger.info("Updating protein level metadata COMPLETED 100%")
    return list_of_project_sub_details


async def find_uniprot_data(list_of_project_sub_details):
    i = 1
    batch_size = 4
    logging.info("Uniprot Batch size: " + str(batch_size))
    base_in_URL = "https://rest.uniprot.org/uniprotkb/search?query=accession:"
    fields_in_URL = "&fields=protein_name,gene_primary&size=50"
    seperator = "%20OR%20"
    accessions = []
    uniprot_records = []
    for sub_details in list_of_project_sub_details:
        accessions.append(sub_details.protein_accession)
        # batch size or last one in the list
        if i % batch_size == 0 or i == len(list_of_project_sub_details):
            complete_URL = ""
            try:
                # extra check not to submit plenty of accessions
                if len(accessions) <= batch_size:
                    accessions_in_URL = seperator.join(accessions)
                    complete_URL = base_in_URL + accessions_in_URL + fields_in_URL
                    logging.info("Calling Uniprot API: " + complete_URL)
                    uniprot_response = requests.get(complete_URL).json()
                    if uniprot_response is not None:
                        logging.info("Number of results found for the query: " + str(len(uniprot_response["results"])))
                        for result in uniprot_response["results"]:
                            uniprot_records.append(result)
                else:
                    raise Exception("Number of accessions are greater than the batch size!")
            except Exception as error:
                logger.error(str(error))
                logger.error(complete_URL + " failed to get data from Uniprot:" + str(error))
            finally:
                accessions = []
        i += 1
    return uniprot_records


async def extract_uniprot_data(list_of_project_sub_details, uniprot_records):
    for sub_details in list_of_project_sub_details:
        for uniprot_result in uniprot_records:
            try:
                if sub_details.protein_accession == uniprot_result["primaryAccession"]:
                    if not uniprot_result["entryType"] == "Inactive":
                        if uniprot_result["proteinDescription"]["recommendedName"] is not None:
                            sub_details.protein_name = \
                                uniprot_result["proteinDescription"]["recommendedName"]["fullName"]["value"]
                        elif uniprot_result["proteinDescription"]["submissionNames"] is not None \
                                and len(uniprot_result["proteinDescription"]["submissionNames"]) > 0:
                            sub_details.protein_name = \
                                uniprot_result["proteinDescription"]["submissionNames"][0]["fullName"]["value"]
                        logger.debug(uniprot_result["primaryAccession"] + " protein name: " + sub_details.protein_name)
                        if uniprot_result["genes"] is None or len(uniprot_result["genes"]) == 0:
                            logger.error("\t" + sub_details.protein_accession + " has no genes section")
                        elif len(uniprot_result["genes"]) > 0:
                            sub_details.gene_name = uniprot_result["genes"][0]["geneName"]["value"]
                            logger.debug(uniprot_result["primaryAccession"] + " gene name   : " + sub_details.gene_name)
                        else:
                            raise Exception("Error in matching genes section of uniprot response")
                    else:
                        logger.warn(uniprot_result["primaryAccession"] + "is Inactive")
            except Exception as error:
                logger.error(str(error))
                logger.error(
                    sub_details.protein_accession + " has an error when trying to match uniprot response:" + str(error))
    return list_of_project_sub_details


async def find_data_availability(list_of_project_sub_details, base_in_URL, resourse):
    for sub_details in list_of_project_sub_details:
        try:
            accession_in_URL = sub_details.protein_accession
            complete_URL = base_in_URL + accession_in_URL
            logging.debug("Calling API: " + complete_URL)
            response = requests.get(complete_URL).json()
            if resourse == "PDBe":
                sub_details.in_pdbe_kb = response is not None and len(response) > 0
            elif resourse == "AlphaFold":
                sub_details.in_alpha_fold_db = response is not None and len(response) > 0
        except Exception as error:
            logger.error(str(error))
            logger.error(complete_URL + " failed to get data from Uniprot:" + str(error))
    return list_of_project_sub_details


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
        with session:
            result = session.execute(sql, sql_values)
            result_list = [
                {'key': row[0], 'value': row[1]} for row in result if len(row) >= 2
            ]
    except Exception as error:
        logger.error(f"Error type: {type(error)}, Error message: {str(error)}")
    finally:
        logger.debug('Database session is closed.')
    return result_list


async def project_per_species_counts(sql, sql_values, session):
    """
    Get table of data in the database according to the SQL
    :param sql_values: SQl Values
    :param sql: SQL to get project accessions
    :param session: database session
    :return: List of key value pairs
    """
    try:
        with session:
            result = session.execute(sql, sql_values)
            result_list = [
                {'organism': row[0], 'count': row[1]} for row in result if len(row) >= 2
            ]
    except Exception as error:
        logger.error(f"Error type: {type(error)}, Error message: {str(error)}")
    finally:
        logger.debug('Database session is closed.')
    return result_list


async def peptide_per_protein_counts(sql, sql_values, session):
    """
    Get table of data in the database according to the SQL
    :param sql_values: SQl Values
    :param sql: SQL to get project accessions
    :param session: database session
    :return: List of key value pairs
    """
    try:
        with session:
            result = session.execute(sql, sql_values)
            result_list = [
                {'protein_frequency': row[0], 'peptide_count': row[1]} for row in result if len(row) >= 2
            ]
    except Exception as error:
        logger.error(f"Error type: {type(error)}, Error message: {str(error)}")
    finally:
        logger.debug('Database session is closed.')
    return result_list


async def get_statistics_count(sql, session):
    """
    Get all the Unique accessions(project, protein) in the database according to the SQL
    :param sql: SQL to get project accessions
    :param session: database session
    :return: List of unique project accessions
    """
    values = None
    try:
        result = session.execute(sql)
        # Fetch the values from the result
        row = result.fetchone()

        statistics_counts = {'Number of Projects': row[0],
                             'Number of proteins': row[1],
                             'Number of peptides': row[2],
                             'Number of spectra': row[3],
                             'Number of species': row[4]}
        print(statistics_counts)
    except Exception as error:
        logger.error(error)
    finally:
        session.close()
        logger.debug('Database session is closed.')
    return statistics_counts


async def get_projects_count(sql, session):
    """
    Get project counts for health check
    :param sql: SQL to get project accessions
    :param session: database session
    :return: count
    """
    try:
        result = session.execute(sql)
        # Fetch the values from the result
        count = result.fetchone()
    except Exception as error:
        logger.error(error)
    finally:
        session.close()
        logger.debug('Database session is closed.')
    return count

