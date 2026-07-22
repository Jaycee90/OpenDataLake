# this file owns configuration and it is the source of truth for all configuration values in the application

# dataclasses generates constructors automatically and makes it easy to create immutable objects
from dataclasses import dataclass
import os
from dotenv import load_dotenv

@dataclass(frozen=True) # once created, the object cannot be modified
class Settings:
    ticketmaster_api_key: str

    http_timeout: float
    http_max_attempts: int
    http_delay: float

    database_url: str

    @classmethod
    def load(cls) -> "Settings":
        load_dotenv()

        database_url = os.getenv("DATABASE_URL")

        if not database_url:
            raise ValueError("DATABASE_URL is required.")
        
        api_key = os.getenv("TICKETMASTER_API_KEY")
        http_timeout=float(os.getenv("HTTP_TIMEOUT", 10.0)),
        http_max_attempts=int(os.getenv("HTTP_MAX_ATTEMPTS", 3)),
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