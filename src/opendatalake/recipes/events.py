import logging
from typing import Any
from datetime import date, time

from opendatalake.recipes.base import BaseRecipe
from opendatalake.database.models.event import Event
from opendatalake.repositories.event_repo import EventRepository
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

    def __init__(self, ticketmaster_service: TicketmasterService, event_repository: EventRepository) -> None:
        self._ticketmaster_service = ticketmaster_service
        self._event_repository = event_repository

    def extract(self) -> list[dict[str, Any]]:
        logger.info("Extracting events for major US cities...")

        all_events: list[dict[str, Any]] = []

        for city in self.CITIES:
            try:
                events = self._ticketmaster_service.get_events(city=city, size=20)
            except TicketmasterError:
                logger.error("Skipping %s due to Ticketmaster API error.", city)
                continue

            for event in events:
                event["requested_city"] = city  # Add the city to each event
            all_events.extend(events)

            logger.info("Received %d events for %s.", len(events), city)
        logger.info("Total events extracted: %d", len(all_events))

        return all_events

    def transform(self, raw_data: list[dict]) -> list[Event]:
        logger.info("Transforming %d events...", len(raw_data))

        transformed_events: list[Event] = []

        for raw_event in raw_data:
            venues = raw_event.get("_embedded", {}).get("venues", [])
            venue = venues[0] if venues else {}

            classifications = raw_event.get("classifications", [])
            classification = classifications[0] if classifications else {}

            start = raw_event.get("dates", {}).get("start", {})
            status = raw_event.get("dates", {}).get("status", {})
            event_date_value = start.get("localDate")
            event_time_value = start.get("localTime")
            event_date=(date.fromisoformat(event_date_value) if event_date_value else None)
            event_time=(time.fromisoformat(event_time_value) if event_time_value else None)

            event_modal = Event(
                event_id=raw_event.get("id"),
                name=raw_event.get("name"),
                event_url=raw_event.get("url"),
                event_date=event_date,
                event_time=event_time,
                status= status.get("code"),
                category= classification.get("segment", {}).get("name"),
                genre= classification.get("genre", {}).get("name"),
                subgenre= classification.get("subGenre", {}).get("name"),
                venue= venue.get("name"),
                city= venue.get("city", {}).get("name"),
                state= venue.get("state", {}).get("stateCode"),
                address= venue.get("address", {}).get("line1"),
                latitude= venue.get("location", {}).get("latitude"),
                longitude= venue.get("location", {}).get("longitude"),
                source= "ticketmaster",
            )

            transformed_events.append(event_modal)

        logger.info("Successfully transformed %d events.", len(transformed_events))
        return transformed_events

    def load(self, transformed_data: list[Event]) -> None:
        logger.info("Loading %d US events...", len(transformed_data))

        self._event_repository.upsert_all(transformed_data)

        logger.info("Loaded %d events", len(transformed_data))