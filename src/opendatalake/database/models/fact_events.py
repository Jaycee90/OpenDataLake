from sqlalchemy import (
    DateTime, ForeignKey, Integer, String, UniqueConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from opendatalake.database.models.base import Base


class FactEvent(Base):
    __tablename__ = "fact_events"
    __table_args__ = {"schema": "analytics"}

    event_key: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    event_id: Mapped[str] = mapped_column(
        String, unique=True, nullable=False
    )

    date_key: Mapped[int] = mapped_column(
        ForeignKey("analytics.dim_date.date_key"),
        nullable=False,
    )

    venue_key: Mapped[int] = mapped_column(
        ForeignKey("analytics.dim_venue.venue_key"),
        nullable=False,
    )

    category_key: Mapped[int] = mapped_column(
        ForeignKey("analytics.dim_category.category_key"),
        nullable=False,
    )

    event_name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )