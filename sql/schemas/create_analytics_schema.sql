-- Run manually to create schema with the following command:
-- psql -d opendatalake -f sql/schemas/create_analytics_schema.sql
-- however, alembic will create the schema automatically when running migrations.
-- how alembic will read this file???? to find out..
CREATE SCHEMA IF NOT EXISTS analytics;
