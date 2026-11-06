import os

SECRET_KEY = os.environ["SUPERSET_SECRET_KEY"] # reads the secret you generated rather than hardcoding it.

# tells Superset where to store its own users, charts, dashboards, and configuration.
# /app/superset_home/ will be backed by your superset_home Docker volume.
# The existing OpenDataLake PostgreSQL database remains separate and untouched.
# /app/superset_home/ : is a directory inside the Docker container, not a folder on your Mac.
SQLALCHEMY_DATABASE_URI = (
    "sqlite:////app/superset_home/superset.db"
)