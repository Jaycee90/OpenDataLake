"""add yearly events by city view

Revision ID: 4f59099a5afb
Revises: a6a29d42b214
"""

from pathlib import Path
from typing import Sequence, Union

from alembic import op

revision: str = "4f59099a5afb"
down_revision: Union[str, Sequence[str], None] = "a6a29d42b214"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the yearly events by city view."""
    sql_file = (
        Path(__file__).resolve().parents[2]
        / "sql"
        / "views"
        / "warehouse_events_by_year_and_city.sql"
    )

    op.execute(sql_file.read_text())


def downgrade() -> None:
    """Remove the yearly events by city view."""
    op.execute(
        "DROP VIEW IF EXISTS analytics.warehouse_events_by_year_and_city;"
    )