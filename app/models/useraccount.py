from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Text, TIMESTAMP, Integer
from app.models.base import Base
import datetime


class UserAccount(Base):
    __tablename__ = 'useraccount'
    id: Mapped[str] = mapped_column(Integer, primary_key=True, nullable=False)
    user_name: Mapped[str] = mapped_column(Text, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    gdpr_token: Mapped[str] = mapped_column(Text, nullable=True)
    ptoken: Mapped[str] = mapped_column(Text, nullable=True)
    ptoken_timestamp: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=True)
    gdpr_timestamp: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=True)
    quote = False
