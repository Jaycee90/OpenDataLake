from sqlalchemy import select, func

from opendatalake.config.settings import Settings
from opendatalake.database.database_session import create_database_engine
from opendatalake.database.models.event import Event
from opendatalake.database.models.fact_events import FactEvent
from opendatalake.database.repositories.warehouse_repository import WarehouseRepository
from tests.factories.event_factory import create_event
from datetime import date
from opendatalake.database.models.dim_date import DimDate
from opendatalake.database.models.dim_venue import DimVenue
from opendatalake.database.models.dim_category import DimCategory

'''It verifies that two source events can exist while only one is loaded into the fact table.

The outer transaction rolls back the inserted data, including the dimensions and fact record.

Important: This test must run only against opendatalake_test. The database-name assertion 
provides an additional safeguard, but the test still needs to connect before checking it.'''

def test_load_facts_filters_event_ids():
    engine = create_database_engine(Settings.load())

    try:
        # Prevent accidentally testing against the development database.
        assert engine.url.database == "opendatalake_test"

        with engine.connect() as connection:
            transaction = connection.begin()

            try:
                from sqlalchemy.orm import Session

                with Session(bind=connection, autoflush=False) as session:
                    # Create two sample events.
                    event1 = create_event(event_id="test-event-1")
                    event2 = create_event(event_id="test-event-2")

                    session.add_all([event1, event2])
                    session.flush()

                    warehouse = WarehouseRepository(session)

                    # Load dimensions required by the fact table.
                    warehouse.load_dates()
                    warehouse.load_venues()
                    warehouse.load_categories()

                    # Load only the first event into the fact table.
                    inserted = warehouse.load_facts(
                        event_ids=["test-event-1"]
                    )

                    assert inserted == 1

                    # Verify only the selected event was loaded.
                    fact_ids = session.scalars(
                        select(FactEvent.event_id)
                    ).all()

                    assert fact_ids == ["test-event-1"]

                    # Confirm both source events exist.
                    source_count = session.scalar(
                        select(func.count()).select_from(Event)
                    )

                    assert source_count == 2

            finally:
                # Undo all test inserts.
                transaction.rollback()

    finally:
        engine.dispose()

def test_load_dates_filters_event_ids():
    engine = create_database_engine(Settings.load())

    try:
        assert engine.url.database == "opendatalake_test"

        with engine.connect() as connection:
            transaction = connection.begin()

            try:
                from sqlalchemy.orm import Session

                with Session(bind=connection, autoflush=False) as session:
                    event1 = create_event(
                        event_id="date-test-1",
                        event_date=date(2026, 12, 10),
                    )

                    event2 = create_event(
                        event_id="date-test-2",
                        event_date=date(2026, 12, 20),
                    )

                    session.add_all([event1, event2])
                    session.flush()

                    warehouse = WarehouseRepository(session)

                    inserted = warehouse.load_dates(
                        event_ids=["date-test-1"]
                    )

                    assert inserted == 1

                    dates = session.scalars(
                        select(DimDate.full_date)
                    ).all()

                    assert dates == [date(2026, 12, 10)]

            finally:
                transaction.rollback()

    finally:
        engine.dispose()

def test_load_venues_filters_event_ids():
    engine = create_database_engine(Settings.load())

    try:
        assert engine.url.database == "opendatalake_test"

        with engine.connect() as connection:
            transaction = connection.begin()

            try:
                from sqlalchemy.orm import Session

                with Session(bind=connection, autoflush=False) as session:
                    event1 = create_event(
                        event_id="venue-test-1",
                        venue="Moody Center",
                        city="Austin",
                    )

                    event2 = create_event(
                        event_id="venue-test-2",
                        venue="Toyota Center",
                        city="Houston",
                    )

                    session.add_all([event1, event2])
                    session.flush()

                    warehouse = WarehouseRepository(session)

                    inserted = warehouse.load_venues(
                        event_ids=["venue-test-1"]
                    )

                    assert inserted == 1

                    venues = session.scalars(
                        select(DimVenue.venue_name)
                    ).all()

                    assert venues == ["Moody Center"]

            finally:
                transaction.rollback()

    finally:
        engine.dispose()

def test_load_categories_filters_event_ids():
    engine = create_database_engine(Settings.load())

    try:
        assert engine.url.database == "opendatalake_test"

        with engine.connect() as connection:
            transaction = connection.begin()

            try:
                from sqlalchemy.orm import Session

                with Session(bind=connection, autoflush=False) as session:
                    event1 = create_event(
                        event_id="category-test-1",
                        category="Music",
                        genre="Rock",
                        subgenre="Alternative",
                    )

                    event2 = create_event(
                        event_id="category-test-2",
                        category="Sports",
                        genre="Basketball",
                        subgenre="NBA",
                    )

                    session.add_all([event1, event2])
                    session.flush()

                    warehouse = WarehouseRepository(session)

                    inserted = warehouse.load_categories(
                        event_ids=["category-test-1"]
                    )

                    assert inserted == 1

                    categories = session.scalars(
                        select(DimCategory.category)
                    ).all()

                    assert categories == ["Music"]

            finally:
                transaction.rollback()

    finally:
        engine.dispose()