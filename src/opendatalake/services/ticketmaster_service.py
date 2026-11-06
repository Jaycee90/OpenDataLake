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

    def get_events(self, city: str, state: str, size: int = 50, page: int = 0, start_date: str | None = None, end_date: str | None = None) -> list[dict[str, Any]]:
        logger.info("Calling Ticketmaster API for %s, %s (page %d)", city, state, page)

        params={
            "apikey": self.settings.ticketmaster_api_key,
            "city": city,
            "stateCode": state,
            "countryCode": "US",
            "size": size,
            "page": page,
            "sort": "date,asc",
        }

        if start_date is not None:
            params["startDateTime"] = start_date

        if end_date is not None:
            params["endDateTime"] = end_date

        try:
            response_data = self.http_client.get_json(
                url=self.EVENTS_URL,
                params=params,
            )
        except HttpClientError as e:
            raise TicketmasterError(f"Failed to retrieve Ticketmaster events for {city}, {state}") from e

        logger.info(
            "Ticketmaster pagination metadata for %s, %s: %s",
            city,
            state,
            response_data.get("page", {}),
        )
        embedded = response_data.get("_embedded", {})
        events = embedded.get("events", [])

        logger.info("Ticketmaster API returned %d events for %s, %s", len(events), city, state)
        
        return events

    def get_event_page(
        self,
        city: str,
        state: str,
        start_date_time: str,
        end_date_time: str,
        size: int = 50,
        page: int = 0,
    ) -> dict[str, Any]:
        params = {
            "apikey": self.settings.ticketmaster_api_key,
            "city": city,
            "stateCode": state,
            "countryCode": "US",
            "size": size,
            "page": page,
            "sort": "date,asc",
            "startDateTime": start_date_time,
            "endDateTime": end_date_time,
        }

        try:
            return self.http_client.get_json(
                url=self.EVENTS_URL,
                params=params,
            )
        except HttpClientError as e:
            raise TicketmasterError(
                f"Failed to retrieve Ticketmaster events for {city}, {state}"
            ) from e