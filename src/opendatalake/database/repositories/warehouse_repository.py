from sqlalchemy import select, tuple_
from sqlalchemy.orm import Session
import logging
from opendatalake.database.models.event import Event
from opendatalake.database.models.dim_date import DimDate
from opendatalake.database.models.dim_venue import DimVenue
from opendatalake.database.models.dim_category import DimCategory
from opendatalake.database.models.fact_events import FactEvent
from sqlalchemy import delete


logger = logging.getLogger(__name__)

# Maximum number of event IDs processed in a single database query.
BATCH_SIZE = 1000


def batch_event_ids(event_ids: list[str]):
    """Split event IDs into smaller batches to avoid oversized SQL queries."""
    for start in range(0, len(event_ids), BATCH_SIZE):
        yield event_ids[start:start + BATCH_SIZE]

class WarehouseRepository:

    def __init__(self, session: Session):
        self.session = session

    def clear_warehouse(self) -> None:
        """
        Clear warehouse tables before a full ETL refresh.

        Must be called inside the same transaction used
        to load the new snapshot.
        """

        # Delete facts first because they reference dimensions.
        self.session.execute(delete(FactEvent))

        # Then delete dimensions.
        self.session.execute(delete(DimVenue))
        self.session.execute(delete(DimCategory))
        self.session.execute(delete(DimDate))

        self.session.flush()

        logger.info("Existing warehouse data cleared.")

    def load_dates(self, event_ids: list[str] | None = None) -> int:
        query = select(Event.event_date).where(
            Event.event_date.is_not(None)
        )

        if event_ids is not None:
            if not event_ids:
                return 0

            # Retrieve dates in batches to avoid oversized SQL queries.
            event_dates = set()

            for batch in batch_event_ids(event_ids):
                batch_query = query.where(
                    Event.event_id.in_(batch)
                ).distinct()

                event_dates.update(
                    self.session.scalars(batch_query).all()
                )
        else:
            event_dates = set(
                self.session.scalars(query.distinct()).all()
            )

        inserted = 0

        for event_date in event_dates:
            date_key = int(event_date.strftime("%Y%m%d"))

            if self.session.get(DimDate, date_key):
                continue

            self.session.add(
                DimDate(
                    date_key=date_key,
                    full_date=event_date,
                    year=event_date.year,
                    month=event_date.month,
                    month_name=event_date.strftime("%B"),
                    quarter=(event_date.month - 1) // 3 + 1,
                    day_of_week=event_date.strftime("%A"),
                )
            )
            inserted += 1

        self.session.flush()
        return inserted
    
    '''
    select() reads venue information from public.events.
    .distinct() removes identical source rows.
    session.scalar() checks whether a venue already exists.
    session.add() prepares a new venue record.
    session.flush() sends inserts to PostgreSQL without committing the transaction.
    '''
    def load_venues(self, event_ids: list[str] | None = None) -> int:
        query = (
            select(
                Event.venue,
                Event.city,
                Event.state,
                Event.address,
                Event.latitude,
                Event.longitude,
            )
            .where(
                Event.venue.is_not(None),
                Event.city.is_not(None),
            )
        )

        if event_ids is not None:
            if not event_ids:
                return 0

            # Retrieve venues in smaller batches.
            venues = []

            for batch in batch_event_ids(event_ids):
                batch_query = query.where(
                    Event.event_id.in_(batch)
                )

                venues.extend(self.session.execute(batch_query.order_by(Event.id)).all())
        else:
            venues = self.session.execute(query.order_by(Event.id)).all()

        inserted = 0
        seen = set()

        for venue in venues:
            identity = (venue.venue, venue.city, venue.state)

            # Skip repeated venue identities in this batch.
            if identity in seen:
                continue

            seen.add(identity)

            # Skip venues already stored in PostgreSQL.
            existing = self.session.scalar(
                select(DimVenue).where(
                    DimVenue.venue_name == venue.venue,
                    DimVenue.city == venue.city,
                    DimVenue.state == venue.state,
                )
            )

            if existing is not None:
                continue

            self.session.add(
                DimVenue(
                    venue_name=venue.venue,
                    city=venue.city,
                    state=venue.state,
                    address=venue.address,
                    latitude=venue.latitude,
                    longitude=venue.longitude,
                )
            )

            inserted += 1

        self.session.flush()
        return inserted

    def load_categories(self, event_ids: list[str] | None = None) -> int:
        query = select(
            Event.category,
            Event.genre,
            Event.subgenre,
        )

        if event_ids is not None:
            if not event_ids:
                return 0

            # Retrieve categories in smaller batches.
            categories = set()

            for batch in batch_event_ids(event_ids):
                batch_query = query.where(
                    Event.event_id.in_(batch)
                ).distinct()

                categories.update(
                    self.session.execute(batch_query).all()
                )
        else:
            categories = set(
                self.session.execute(query.distinct()).all()
            )

        inserted = 0

        for category, genre, subgenre in categories:
            existing = self.session.scalar(
                select(DimCategory).where(
                    DimCategory.category == category,
                    DimCategory.genre == genre,
                    DimCategory.subgenre == subgenre,
                )
            )

            if existing is not None:
                continue

            self.session.add(
                DimCategory(
                    category=category,
                    genre=genre,
                    subgenre=subgenre,
                )
            )

            # Make this row visible to subsequent queries,
            # since our session uses autoflush=False.
            self.session.flush()
            inserted += 1

        return inserted

    def load_facts(self, event_ids: list[str] | None = None) -> int:
        query = select(Event)

        if event_ids is not None:
            if not event_ids:
                return 0
            
            # Retrieve events in batches to avoid oversized SQL queries.
            events = []

            for batch in batch_event_ids(event_ids):
                batch_query = query.where(
                    Event.event_id.in_(batch)
                )

                events.extend(
                    self.session.scalars(batch_query).all()
                )
        else:
            events = self.session.scalars(query).all()

        # Load venue dimension keys once to avoid querying for every event.
        venue_rows = self.session.execute(
            select(
                DimVenue.venue_name,
                DimVenue.city,
                DimVenue.state,
                DimVenue.venue_key,
            )
        ).all()

        venue_lookup = {
            (row.venue_name, row.city, row.state): row.venue_key
            for row in venue_rows
        }

        # Load category dimension keys once to avoid querying for every event.
        category_rows = self.session.execute(
            select(
                DimCategory.category,
                DimCategory.genre,
                DimCategory.subgenre,
                DimCategory.category_key,
            )
        ).all()

        category_lookup = {
            (row.category, row.genre, row.subgenre): row.category_key
            for row in category_rows
        }

        # Load existing fact records once to avoid querying per event.
        existing_facts = {
            fact.event_id: fact
            for fact in self.session.scalars(
                select(FactEvent)
            ).all()
        }
        
        inserted = 0

        for event in events:
            if event.event_date is None:
                logger.warning(
                    "Skipping warehouse fact for event %s: missing date",
                    event.event_id,
                )
                continue
            date_key = int(event.event_date.strftime("%Y%m%d"))

            # Look up the venue key in memory instead of querying PostgreSQL.
            venue_key = venue_lookup.get(
                (event.venue, event.city, event.state)
            )

            # Look up the category key in memory.
            category_key = category_lookup.get(
                (event.category, event.genre, event.subgenre)
            )

            if venue_key is None or category_key is None:
                raise ValueError(
                    f"Missing warehouse dimension for event {event.event_id}"
                )

            # Find the existing fact record in memory instead of querying PostgreSQL.
            existing = existing_facts.get(event.event_id)

            if existing is not None:
                existing.date_key = date_key
                existing.venue_key = venue_key
                existing.category_key = category_key
                existing.event_name = event.name
                existing.status = event.status
                continue

            self.session.add(
                FactEvent(
                    event_id=event.event_id,
                    date_key=date_key,
                    venue_key=venue_key,
                    category_key=category_key,
                    event_name=event.name,
                    status=event.status,
                )
            )

            inserted += 1

        self.session.flush()
        return inserted