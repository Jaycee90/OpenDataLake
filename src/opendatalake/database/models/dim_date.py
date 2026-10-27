from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from opendatalake.database.models.base import Base


class DimDate(Base):
    __tablename__ = "dim_date"
    __table_args__ = {"schema": "analytics"}

    date_key: Mapped[int] = mapped_column(Integer, primary_key=True,)
    full_date: Mapped[date] = mapped_column(Date, unique=True, nullable=False,)
    year: Mapped[int] = mapped_column(Integer)
    month: Mapped[int] = mapped_column(Integer)
    month_name: Mapped[str] = mapped_column(String)
    quarter: Mapped[int] = mapped_column(Integer)
    day_of_week: Mapped[str] = mapped_column(String)