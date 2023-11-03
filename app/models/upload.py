from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text, JSON, BOOLEAN, TIMESTAMP, func, Integer
from app.models.base import Base
from app.models.useraccount import UserAccount
from app.models.misc.guid import GUID
from typing import Optional, Any
import datetime


class Upload(Base):
    __tablename__ = "upload"
    id: Mapped[str] = mapped_column(GUID, primary_key=True, nullable=False)
    user_id: Mapped[str] = mapped_column(GUID, ForeignKey("useraccount.id"), nullable=True)
    project_id: Mapped[str] = mapped_column(Text, nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    pubmed_id: Mapped[str] = mapped_column(Text, nullable=True)
    number_of_proteins: Mapped[int] = mapped_column(Integer, nullable=True)
    number_of_peptides: Mapped[int] = mapped_column(Integer, nullable=True)
    number_of_spectra: Mapped[int] = mapped_column(Integer, nullable=True)
    identification_file_name: Mapped[str] = mapped_column(Text, nullable=False)
    provider: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    audits: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    samples: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    bib: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    spectra_formats: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)  # nullable=False
    upload_time: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    contains_crosslinks: Mapped[bool] = mapped_column(BOOLEAN, nullable=True)  # nullable=False
    upload_error: Mapped[str] = mapped_column(Text, nullable=True)  # nullable=False
    error_type: Mapped[str] = mapped_column(Text, nullable=True)  # nullable=False
    upload_warnings: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)  # nullable=False
    identification_file_name_clean: Mapped[str] = mapped_column(Text, nullable=True)
    quote = False

    user = relationship('UserAccount', backref='uploads')

