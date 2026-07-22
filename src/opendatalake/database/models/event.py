from datetime import date, time, datetime

from sqlalchemy import Date, String, Time, DateTime, func, String, Float
from sqlalchemy.orm import Mapped, mapped_column

from opendatalake.database.models.base import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String)
    event_url: Mapped[str | None] = mapped_column(String, nullable=True,)
    event_date: Mapped[date | None] = mapped_column(Date, nullable=True,)
    event_time: Mapped[time | None] = mapped_column(Time, nullable=True,)
    status: Mapped[str | None] = mapped_column(String, nullable=True,)
    category: Mapped[str | None] = mapped_column(String, nullable=True,)
    genre: Mapped[str | None] = mapped_column(String, nullable=True,)
    subgenre: Mapped[str | None] = mapped_column(String, nullable=True,)
    venue: Mapped[str | None] = mapped_column(String, nullable=True,)
    city: Mapped[str | None] = mapped_column(String, nullable=True,)
    state: Mapped[str | None] = mapped_column(String, nullable=True,)
    address: Mapped[str | None] = mapped_column(String, nullable=True,)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True,)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True,)
    source: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
