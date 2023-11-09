from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Text, JSON, Integer
from app.models.base import Base
from typing import Optional, Any


class SpectrumIdentificationProtocol(Base):
    __tablename__ = "spectrumidentificationprotocol"
    id: Mapped[str] = mapped_column(Text, primary_key=True, nullable=False)
    upload_id: Mapped[str] = mapped_column(Integer, ForeignKey("upload.id"), index=True, primary_key=True, nullable=False)
    frag_tol: Mapped[str] = mapped_column(Text, nullable=False)
    search_params: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    analysis_software: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    quote = False

