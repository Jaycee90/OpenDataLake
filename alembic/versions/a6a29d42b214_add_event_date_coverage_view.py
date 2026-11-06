"""add event date coverage view

Revision ID: a6a29d42b214
Revises: bb10c6be1c01
Create Date: 2026-10-29 12:13:35.088726

"""
from typing import Sequence, Union

from alembic import op
from pathlib import Path


# revision identifiers, used by Alembic.
revision: str = 'a6a29d42b214'
down_revision: Union[str, Sequence[str], None] = 'bb10c6be1c01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

'''
1. Path(__file__) identifies the migration file.
2. .parents[2] navigates to your OpenDataLake project root.
3. The path points to sql/views/event_date_coverage.sql.
4. op.execute() executes that SQL in PostgreSQL.
downgrade(): Removes the view if you roll back this migration.
'''
def upgrade() -> None:
    """Create the event date coverage view."""
    sql_file = (
        Path(__file__).resolve().parents[2]
        / "sql"
        / "views"
        / "event_date_coverage.sql"
    )

    op.execute(sql_file.read_text())


def downgrade() -> None:
    """Remove the event date coverage view."""
    op.execute(
        "DROP VIEW IF EXISTS analytics.event_date_coverage;"
    )