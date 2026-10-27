"""add analytics reporting views

Revision ID: bb10c6be1c01
Revises: 3bcf6e60f406
Create Date: 2026-10-27 13:48:57.681606

"""
from typing import Sequence, Union
from pathlib import Path
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'bb10c6be1c01'
down_revision: Union[str, Sequence[str], None] = '3bcf6e60f406'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    project_root = Path(__file__).resolve().parents[2]

    sql_files = [
        "views/events_by_city.sql",
        "views/events_by_category.sql",
        "views/events_by_month.sql",
        "materialized_views/event_counts_by_city_and_month.sql",
        "materialized_views/top_categories_by_city.sql",
    ]

    for filename in sql_files:
        sql_path = project_root / "sql" / filename
        op.execute(sql_path.read_text(encoding="utf-8"))


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS analytics.top_categories_by_city")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS analytics.event_counts_by_city_and_month")

    op.execute("DROP VIEW IF EXISTS analytics.warehouse_events_by_month")
    op.execute("DROP VIEW IF EXISTS analytics.warehouse_events_by_category")
    op.execute("DROP VIEW IF EXISTS analytics.warehouse_events_by_city")