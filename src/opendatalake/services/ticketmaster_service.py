from opendatalake.config.settings import Settings
from opendatalake.services.http_client import HttpClient
from typing import Any

class TicketmasterService:
    EVENTS_URL = "https://app.ticketmaster.com/discovery/v2/events.json"

    def __init__(self, http_client: HttpClient, settings: Settings) -> None:
        self.http_client = http_client
        self.settings = settings

    def get_events(self, city: str, size: int = 20) -> list[dict[str, Any]]:
        print(f"Calling Ticketmaster API for {city}")

        response_data = self.http_client.get_json(url=self.EVENTS_URL, params={
            "apikey": self.settings.ticketmaster_api_key,
            "city": city,
            "size": size,
            "sort": "date,asc",
        },
        )
        embedded = response_data.get("_embedded", {})
        events = embedded.get("events", [])

        return events