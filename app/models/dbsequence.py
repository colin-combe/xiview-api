from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Text
from app.models.base import Base
from app.models.misc.guid import GUID


class DBSequence(Base):
    __tablename__ = "dbsequence"
    id: Mapped[str] = mapped_column(Text, primary_key=True, nullable=False)
    upload_id: Mapped[str] = mapped_column(GUID, ForeignKey("upload.id"), primary_key=True, nullable=False)
    accession: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    sequence: Mapped[str] = mapped_column(Text, nullable=True)
    quote = False
