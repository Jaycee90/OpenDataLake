import logging
from typing import Any

from opendatalake.config.settings import Settings
from opendatalake.services.http_client import HttpClient
from opendatalake.exceptions.http_client_error import HttpClientError
from opendatalake.exceptions.ticketmaster_error import TicketmasterError

logger = logging.getLogger(__name__)

class TicketmasterService:
    EVENTS_URL = "https://app.ticketmaster.com/discovery/v2/events.json"

    def __init__(self, http_client: HttpClient, settings: Settings) -> None:
        self.http_client = http_client
        self.settings = settings

    def get_events(self, city: str, size: int = 20) -> list[dict[str, Any]]:
        logger.info(f"Calling Ticketmaster API for {city}")

        try:
            response_data = self.http_client.get_json(
                url=self.EVENTS_URL,
                params={
                    "apikey": self.settings.ticketmaster_api_key,
                    "city": city,
                    "size": size,
                    "sort": "date,asc",
                },
            )
        except HttpClientError as e:
            raise TicketmasterError(f"Failed to retrieve Ticketmaster events for {city}") from e

        embedded = response_data.get("_embedded", {})
        events = embedded.get("events", [])

        logger.info("Ticketmaster API returned %d events for %s", len(events), city)
        
        return events