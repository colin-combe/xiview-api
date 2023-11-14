from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text, Integer
from app.models.base import Base


class ProjectDetails(Base):
    __tablename__ = "projectdetails"
    id: Mapped[str] = mapped_column(Integer, primary_key=True,  autoincrement=True, nullable=False)
    user_id: Mapped[str] = mapped_column(Integer, ForeignKey("useraccount.id"), nullable=True)
    project_id: Mapped[str] = mapped_column(Text, nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    pubmed_id: Mapped[str] = mapped_column(Text, nullable=True)
    number_of_proteins: Mapped[int] = mapped_column(Integer, nullable=True)
    number_of_peptides: Mapped[int] = mapped_column(Integer, nullable=True)
    number_of_spectra: Mapped[int] = mapped_column(Integer, nullable=True)
    quote = False

    user = relationship('UserAccount', backref='uploads')
