import logging
from typing import Any
from datetime import date, time
from sqlalchemy.orm import Session, sessionmaker
from opendatalake.recipes.base import BaseRecipe
from opendatalake.database.models.event import Event
from opendatalake.repositories.event_repo import EventRepository
from opendatalake.services.ticketmaster_service import TicketmasterService
from opendatalake.exceptions.ticketmaster_error import TicketmasterError
from opendatalake.repositories.analytics_repo import AnalyticsRepository
from opendatalake.database.repositories.warehouse_repository import WarehouseRepository

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

    def __init__(self, ticketmaster_service: TicketmasterService, event_repository: EventRepository, analytics_repository: AnalyticsRepository, session_factory: sessionmaker[Session]) -> None:
        self._ticketmaster_service = ticketmaster_service
        self._event_repository = event_repository
        self._analytics_repository = analytics_repository
        self._session_factory = session_factory

    # def extract(self) -> list[dict[str, Any]]:
    #     logger.info("Extracting events for major US cities...")

    #     all_events: list[dict[str, Any]] = []

    #     for city in self.CITIES:
    #         try:
    #             events = self._ticketmaster_service.get_events(city=city, size=20)
    #         except TicketmasterError:
    #             logger.error("Skipping %s due to Ticketmaster API error.", city)
    #             continue

    #         for event in events:
    #             event["requested_city"] = city  # Add the city to each event
    #         all_events.extend(events)

    #         logger.info("Received %d events for %s.", len(events), city)
    #     logger.info("Total events extracted: %d", len(all_events))

    #     return all_events

    # Switching to a paginated approach for extracting events from Ticketmaster API (end of test)
    def extract(self) -> list[dict[str, Any]]:
        logger.info("Extracting events for major US cities...")

        all_events: list[dict[str, Any]] = []

        for city in self.CITIES:
            page = 0
            while True:
                try:
                    events = self._ticketmaster_service.get_events(city=city, size=50, page=page)
                    if not events:  # Break if no more events are returned
                        break
                except TicketmasterError:
                    logger.error("Skipping %s due to Ticketmaster API error.", city)
                    break

                for event in events:
                    event["requested_city"] = city  # Add the city to each event
                all_events.extend(events)

                logger.info("Received %d events for %s on page %d.", len(events), city, page)
                page += 1  # Increment the page number for the next request

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
            # Normalize location data before saving it.
            city = venue.get("city", {}).get("name")
            state = venue.get("state", {}).get("stateCode")

            city = city.strip() if city else None
            state = state.strip() if state else None

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
                city= city,
                state= state,
                address= venue.get("address", {}).get("line1"),
                latitude= venue.get("location", {}).get("latitude"),
                longitude= venue.get("location", {}).get("longitude"),
                source= "ticketmaster",
            )

            transformed_events.append(event_modal)

        logger.info("Successfully transformed %d events.", len(transformed_events))
        return transformed_events
    
    def validate(self, events: list[Event]) -> None:
        if not events:
            raise ValueError("No events were returned")

        seen_event_ids: set[str] = set()

        for event in events:
            if not event.event_id:
                raise ValueError("Event ID cannot be empty")

            if not event.name:
                raise ValueError(
                    f"Event {event.event_id} has no name"
                )

            if not event.city:
                raise ValueError(
                    f"Event {event.event_id} has no city"
                )

            if not event.event_date:
                raise ValueError(
                    f"Event {event.event_id} has no date"
                )

            if event.event_id in seen_event_ids:
                raise ValueError(
                    f"Duplicate event ID: {event.event_id}"
                )

            seen_event_ids.add(event.event_id)

    def load(self, transformed_data: list[Event]) -> None:
        logger.info("Loading %d US events...", len(transformed_data))

        with self._session_factory.begin() as session:
            # Step 1: Load source events.
            self._event_repository.upsert_all(
                transformed_data,
                session=session,
            )

            logger.info("Loaded %d events", len(transformed_data))

            # Step 2: Load warehouse dimensions and facts.
            warehouse = WarehouseRepository(session)

            dates = warehouse.load_dates()
            venues = warehouse.load_venues()
            categories = warehouse.load_categories()
            facts = warehouse.load_facts()

            logger.info(
                "Warehouse loaded: %d dates, %d venues, "
                "%d categories, %d facts",
                dates,
                venues,
                categories,
                facts,
            )

            # Step 3: Refresh analytics materialized views.
            self._analytics_repository.refresh_all(session=session)

            logger.info("Refreshed all analytics materialized views.")