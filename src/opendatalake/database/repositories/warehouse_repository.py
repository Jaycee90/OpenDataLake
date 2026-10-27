from sqlalchemy import select, tuple_
from sqlalchemy.orm import Session

from opendatalake.database.models.event import Event
from opendatalake.database.models.dim_date import DimDate
from opendatalake.database.models.dim_venue import DimVenue
from opendatalake.database.models.dim_category import DimCategory
from opendatalake.database.models.fact_events import FactEvent


class WarehouseRepository:
    def __init__(self, session: Session):
        self.session = session

    def load_dates(self) -> int:
        event_dates = self.session.scalars(
            select(Event.event_date)
            .where(Event.event_date.is_not(None))
            .distinct()
        ).all()

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
    def load_venues(self) -> int:
        venues = self.session.execute(
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
                Event.city.is_not(None)
            )
            .order_by(Event.id)
        ).all()

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

    def load_categories(self) -> int:
        categories = self.session.execute(
            select(
                Event.category,
                Event.genre,
                Event.subgenre,
            ).distinct()
        ).all()

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

    def load_facts(self) -> int:
        events = self.session.scalars(select(Event)).all()
        inserted = 0

        for event in events:
            # Prevent duplicate fact records.
            existing = self.session.scalar(
                select(FactEvent).where(
                    FactEvent.event_id == event.event_id
                )
            )

            if existing is not None:
                continue

            date_key = int(event.event_date.strftime("%Y%m%d"))

            venue_key = self.session.scalar(
                select(DimVenue.venue_key).where(
                    DimVenue.venue_name == event.venue,
                    DimVenue.city == event.city,
                    DimVenue.state == event.state,
                )
            )

            category_key = self.session.scalar(
                select(DimCategory.category_key).where(
                    DimCategory.category == event.category,
                    DimCategory.genre == event.genre,
                    DimCategory.subgenre == event.subgenre,
                )
            )

            if venue_key is None or category_key is None:
                raise ValueError(
                    f"Missing warehouse dimension for event {event.event_id}"
                )

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