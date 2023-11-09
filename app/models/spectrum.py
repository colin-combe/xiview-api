from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Text, LargeBinary, SMALLINT, FLOAT
from app.models.base import Base
from app.models.misc.guid import GUID


class Spectrum(Base):
    __tablename__ = "spectrum"
    id: Mapped[str] = mapped_column(Text, primary_key=True, nullable=False)  # spectrumID from mzID
    spectra_data_ref: Mapped[str] = mapped_column(Text, primary_key=True, nullable=False)
    upload_id: Mapped[str] = mapped_column(GUID, ForeignKey("upload.id"), primary_key=True, index=True, nullable=False)
    peak_list_file_name: Mapped[str] = mapped_column(Text, nullable=False)
    precursor_mz: Mapped[float] = mapped_column(FLOAT, nullable=False)
    precursor_charge: Mapped[int] = mapped_column(SMALLINT, nullable=True)
    mz: Mapped[str] = mapped_column(LargeBinary, nullable=False)
    intensity: Mapped[str] = mapped_column(LargeBinary, nullable=False)
    retention_time: Mapped[float] = mapped_column(FLOAT, nullable=True)
    quote = False

