from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text, Integer
from app.models.base import Base


class ProjectSubDetail(Base):
    __tablename__ = "projectsubdetails"
    id: Mapped[str] = mapped_column(Integer, primary_key=True,  autoincrement=True, nullable=False)
    project_detail_id: Mapped[int] = mapped_column(Integer, ForeignKey('projectdetails.id'), nullable=False)
    protein_db_ref: Mapped[str] = mapped_column(Text, nullable=False)
    protein_name: Mapped[str] = mapped_column(Text, nullable=True)
    gene_name: Mapped[str] = mapped_column(Text, nullable=True)
    protein_accession: Mapped[str] = mapped_column(Text, nullable=False)
    number_of_peptides: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    number_of_cross_links: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    link_to_pdbe: Mapped[str] = mapped_column(Text, nullable=True)
    quote = False

    project_detail = relationship('ProjectDetail', back_populates='project_sub_details')
