from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from opendatalake.database.models.base import Base


class DimCategory(Base):
    __tablename__ = "dim_category"
    __table_args__ = (
        UniqueConstraint("category", "genre", "subgenre", name="uq_dim_category"),
        {"schema": "analytics"},
    )

    category_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String, nullable=False)
    genre: Mapped[str | None] = mapped_column(String, nullable=True)
    subgenre: Mapped[str | None] = mapped_column(String, nullable=True)