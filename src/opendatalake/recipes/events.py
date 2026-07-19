import logging
from typing import Any

from opendatalake.recipes.base import BaseRecipe
from opendatalake.services.ticketmaster_service import TicketmasterService
from opendatalake.exceptions.ticketmaster_error import TicketmasterError

logger = logging.getLogger(__name__)

class EventsRecipe(BaseRecipe):
    name = "US_events"

    CITIES = [
        "Austin",
        "New York",
        "Los Angeles",
        "Chicago",
        "Las Vegas",
        "Miami",
        "Nashville",
        "Seattle",
    ]

    def __init__(self, ticketmaster_service: TicketmasterService) -> None:
        self.ticketmaster_service = ticketmaster_service

    def extract(self) -> list[dict[str, Any]]:
        logger.info("Extracting events for major US cities...")

        all_events: list[dict[str, Any]] = []

        for city in self.CITIES:
            try:
                events = self.ticketmaster_service.get_events(city=city, size=20)
            except TicketmasterError:
                logger.error("Skipping %s due to Ticketmaster API error.", city)
                continue

            for event in events:
                event["requested_city"] = city  # Add the city to each event
            all_events.extend(events)

            logger.info("Received %d events for %s.", len(events), city)
        logger.info("Total events extracted: %d", len(all_events))

        return all_events

    def transform(self, raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        logger.info("Transforming %d events...", len(raw_data))

        transformed_events: list[dict[str, Any]] = []

        for event in raw_data:
            venues = event.get("_embedded", {}).get("venues", [])
            venue = venues[0] if venues else {}

            classifications = event.get("classifications", [])
            classification = classifications[0] if classifications else {}

            start = event.get("dates", {}).get("start", {})
            status = event.get("dates", {}).get("status", {})

            transformed_event = {
                "event_id": event.get("id"),
                "name": event.get("name"),
                "event_url": event.get("url"),
                "event_date": start.get("localDate"),
                "event_time": start.get("localTime"),
                "status": status.get("code"),
                "category": classification.get("segment", {}).get("name"),
                "genre": classification.get("genre", {}).get("name"),
                "subgenre": classification.get("subGenre", {}).get("name"),
                "venue": venue.get("name"),
                "city": venue.get("city", {}).get("name"),
                "state": venue.get("state", {}).get("stateCode"),
                "address": venue.get("address", {}).get("line1"),
                "latitude": venue.get("location", {}).get("latitude"),
                "longitude": venue.get("location", {}).get("longitude"),
                "source": "ticketmaster",
            }

            transformed_events.append(transformed_event)

        logger.info("Successfully transformed %d events.", len(transformed_events))
        return transformed_events

    def load(self, transformed_data: list[dict[str, Any]]) -> None:
        logger.info("Loading %d US events...", len(transformed_data))

        for item in transformed_data:
            logger.debug("Transformed event: %s", item)

        logger.info("Loaded %d events", len(transformed_data))