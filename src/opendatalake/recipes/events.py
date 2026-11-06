import logging
import re
from typing import Any
from datetime import datetime, timezone, date, time, timedelta
from opendatalake.utils.date_windows import split_date_window
from sqlalchemy.orm import Session, sessionmaker
from opendatalake.recipes.base import BaseRecipe
from opendatalake.database.models.event import Event
from opendatalake.repositories.event_repo import EventRepository
from opendatalake.services.ticketmaster_service import TicketmasterService
from opendatalake.exceptions.ticketmaster_error import TicketmasterError
from opendatalake.repositories.analytics_repo import AnalyticsRepository
from opendatalake.database.repositories.warehouse_repository import WarehouseRepository
from opendatalake.config.us_cities import US_CITIES

logger = logging.getLogger(__name__)

class EventsRecipe(BaseRecipe):
    name = "US_events"

    CITIES = US_CITIES

    PAGE_SIZE = 50
    MAX_PAGES = 20

    def __init__(self, ticketmaster_service: TicketmasterService, event_repository: EventRepository, analytics_repository: AnalyticsRepository, session_factory: sessionmaker[Session]) -> None:
        self._ticketmaster_service = ticketmaster_service
        self._event_repository = event_repository
        self._analytics_repository = analytics_repository
        self._session_factory = session_factory

    @staticmethod
    def _deduplicate_events(
        events: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Remove duplicate events while preserving their original order."""

        seen_ids: set[str] = set()
        unique_events: list[dict[str, Any]] = []

        for event in events:
            event_id = event.get("id")

            if event_id is None:
                unique_events.append(event)
                continue

            if event_id in seen_ids:
                continue

            seen_ids.add(event_id)
            unique_events.append(event)

        return unique_events

    def _extract_window(
        self,
        city: str,
        state: str,
        start: datetime,
        end: datetime,
    ) -> list[dict[str, Any]]:
        """Extract events within a date window, splitting oversized windows."""

        if (
            start.tzinfo is None
            or end.tzinfo is None
            or start.utcoffset() != timedelta(0)
            or end.utcoffset() != timedelta(0)
        ):
            raise ValueError("Extraction windows must use UTC timestamps")

        if start.microsecond != 0 or end.microsecond != 0:
            raise ValueError("Extraction windows must use whole-second timestamps")

        if start >= end:
            raise ValueError("Extraction window start must be before end")

        api_start = start.strftime("%Y-%m-%dT%H:%M:%SZ")
        api_end = (end - timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

        response = self._ticketmaster_service.get_event_page(
            city=city,
            state=state,
            start_date_time=api_start,
            end_date_time=api_end,
            size=self.PAGE_SIZE,
            page=0,
        )

        page_info = response.get("page", {})
        total_pages = page_info.get("totalPages", 0)

        if total_pages > self.MAX_PAGES:
            logger.info(
                "Splitting %s, %s window %s to %s (%d pages)",
                city,
                state,
                start,
                end,
                total_pages,
            )

            first, second = split_date_window(start, end)

            return (
                self._extract_window(city, state, *first)
                + self._extract_window(city, state, *second)
            )

        events = response.get("_embedded", {}).get("events", [])

        for page in range(1, total_pages):
            next_response = self._ticketmaster_service.get_event_page(
                city=city,
                state=state,
                start_date_time=api_start,
                end_date_time=api_end,
                size=self.PAGE_SIZE,
                page=page,
            )

            page_events = next_response.get("_embedded", {}).get("events", [])
            events.extend(page_events)

        logger.info(
            "Extracted %d events for %s, %s between %s and %s",
            len(events),
            city,
            state,
            start,
            end,
        )

        return events

    # Switching to a paginated approach for extracting events from Ticketmaster API (end of test)
    def extract(self, days_ahead: int=365) -> list[dict[str, Any]]:
        if days_ahead < 1 or days_ahead > 365:
            raise ValueError("days_ahead must be between 1 and 365")
        logger.info("Extracting events for major US cities over the next %d days...", days_ahead)

        start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        end = start + timedelta(days=days_ahead)

        all_events: list[dict[str, Any]] = []

        for index, (city, state) in enumerate(self.CITIES, start=1):
            logger.info(
                "[%d/%d] Starting %s, %s",
                index, len(self.CITIES), city, state
            )

            print(f"[{index}/50] Starting {city}, {state}", flush=True)

            events = self._extract_window(
                city=city,
                state=state,
                start=start,
                end=end,
            )

            for event in events:
                event["requested_city"] = city  # Add the city to each event
                event["requested_state"] = state  # Add the state to each event
            all_events.extend(events)

            print(f"[{index}/50] Finished {city}: {len(events)} events", flush=True)

            logger.info(
                "[%d/%d] Finished %s, %s: %d events | Running total: %d",
                index, len(self.CITIES), city, state,
                len(events), len(all_events)
            )

        all_events = self._deduplicate_events(all_events)

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

            requested_city = raw_event.get("requested_city")
            requested_state = raw_event.get("requested_state")

            if (
                not requested_city
                or not requested_state
                or not city
                or not state
                or re.sub(r"[^\w\s]", "", city).casefold() != re.sub(r"[^\w\s]", "", requested_city).casefold()
                or state.upper() != requested_state.strip().upper()
            ):
                logger.warning(
                    "Skipping event %s: requested=%s (%s), actual=%s (%s)",
                    raw_event.get("id"),
                    requested_city,
                    requested_state,
                    city,
                    state,
                )
                continue

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

            event_ids = [event.event_id for event in transformed_data]
            dates = warehouse.load_dates(event_ids=event_ids)
            venues = warehouse.load_venues(event_ids=event_ids)
            categories = warehouse.load_categories(event_ids=event_ids)
            facts = warehouse.load_facts(event_ids=event_ids)

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