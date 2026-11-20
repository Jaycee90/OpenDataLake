# this file owns configuration and it is the source of truth for all configuration values in the application

# dataclasses generates constructors automatically and makes it easy to create immutable objects
from dataclasses import dataclass
import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL
from opendatalake.services.secrets_manager_service import SecretsManagerService

@dataclass(frozen=True) # once created, the object cannot be modified
class Settings:
    ticketmaster_api_key: str

    http_timeout: float
    http_max_attempts: int
    http_delay: float

    # Application supports two ways to configure the database connection:
    # Locally: Use DATABASE_URL environment variable (e.g., postgresql+psycopg://user:password@host:port/dbname)
    # On ECS: (URL) Use DB_SECRET_ARN and DB_HOST environment variables to retrieve credentials from AWS Secrets Manager.
    database_url: str | URL

    @classmethod
    def load(cls) -> "Settings":
        load_dotenv()

        '''
        On Mac: The existing DATABASE_URL continues to work.
        On ECS Fargate: We'll configure DB_SECRET_ARN and DB_HOST.
        Python retrieves the RDS username and password from Secrets Manager.
        Security: The database password is not hardcoded in Terraform or printed to the logs.
        '''
        database_url = os.getenv("DATABASE_URL")
        secret_arn = os.getenv("DB_SECRET_ARN")

        if secret_arn:
            secrets_service = SecretsManagerService()
            credentials = secrets_service.get_secret(secret_arn)

            database_url = URL.create(
                drivername="postgresql+psycopg",
                username=credentials["username"],
                password=credentials["password"],
                host=os.environ["DB_HOST"],
                port=5432,
                database=os.getenv("DB_NAME", "postgres"),
            )

        elif not database_url:
            raise ValueError(
                "Either DATABASE_URL or DB_SECRET_ARN is required."
            )
        
        api_key = os.getenv("TICKETMASTER_API_KEY")
        http_timeout=float(os.getenv("HTTP_TIMEOUT", 10.0))
        http_max_attempts=int(os.getenv("HTTP_MAX_ATTEMPTS", 3))
        http_delay=float(os.getenv("HTTP_DELAY", 1.0))

        if not api_key:
            raise ValueError("TICKETMASTER_API_KEY is not set in the environment variables.")

        return cls(
            ticketmaster_api_key=api_key,
            http_timeout=http_timeout,
            http_max_attempts=http_max_attempts,
            http_delay=http_delay,
            database_url=database_url
        )