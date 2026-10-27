from sqlalchemy import Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from opendatalake.database.models.base import Base


class DimVenue(Base):
    __tablename__ = "dim_venue"
    __table_args__ = (
        UniqueConstraint("venue_name", "city", "state", name="uq_dim_venue_location"),
        {"schema": "analytics"},
    )

    venue_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True,)
    venue_name: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str | None] = mapped_column(String, nullable=True)
    address: Mapped[str | None] = mapped_column(String, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)