import datetime
from typing import Optional, Any
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Text, TIMESTAMP, JSON, Integer
from app.models.base import Base
from sqlalchemy.sql import func


class Layout(Base):
    __tablename__ = "layout"
    upload_id: Mapped[str] = mapped_column(Integer, ForeignKey("upload.id"), primary_key=True, index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(Integer, ForeignKey("useraccount.id"), primary_key=True, nullable=False)
    time: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=func.now(), primary_key=True, nullable=False)
    layout: Mapped[str] = mapped_column(JSON, nullable=False)
    description: Mapped[Optional[dict[str, Any]]] = mapped_column(Text, nullable=True)
    quote = False
