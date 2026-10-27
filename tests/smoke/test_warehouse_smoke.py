from sqlalchemy import select, func

from opendatalake.config.settings import Settings
from opendatalake.database.database_session import (
    create_database_engine,
    create_session_factory,
)
from opendatalake.database.models.event import Event
from opendatalake.database.models.dim_date import DimDate
from opendatalake.database.models.dim_venue import DimVenue
from opendatalake.database.models.dim_category import DimCategory
from opendatalake.database.models.fact_events import FactEvent
from opendatalake.database.repositories.warehouse_repository import (
    WarehouseRepository,
)

'''
A smoke test is a small set of checks that answers one question:
“Is the system working well enough for us to continue?”
Imagine deploying OpenDataLake application to Kubernetes.
Before running hundreds of tests, you want to know:
- Can the application start?
- Can it connect to PostgreSQL?
- Can it read data?
- Can it perform a basic operation without crashing?
If these checks fail, there's little value in continuing to more expensive tests.
The name comes from hardware testing: turn something on and see whether smoke comes out.
'''

def test_warehouse_date_loading():
    # Load settings and establish the database connection
    settings = Settings.load() # Reads database configuration from environment settings
    engine = create_database_engine(settings) # Creates a SQLAlchemy engine configured to connect to PostgreSQL
    session_factory = create_session_factory(engine) # Creates a factory that produces database sessions

    try:
        # Start a database transaction
        with session_factory.begin() as session:
            # Check that source events exist
            '''
            We already the number of events we have.
            session.scalar() returns the first value from the SQL query, which is the count.
            The SQLAlchemy expression is equivalent to this PostgreSQL query: SELECT COUNT(*) FROM public.events;
            '''
            source_count = session.scalar(
                select(func.count()).select_from(Event)
            )

            '''
            This checks that the source table isn't empty.
            If the count is zero, the test fails with:
            AssertionError: No event found
            '''
            assert source_count > 0, "No event found"

            # Execute the warehouse loader, This is where we execute the actual code we're testing.
            repository = WarehouseRepository(session)
            repository.load_dates()

            # Verify that dates exist. Equivalent PostgreSQL query: SELECT COUNT(*) FROM analytics.dim_date;
            date_count = session.scalar(
                select(func.count()).select_from(DimDate)
            )

            assert date_count > 0, "No dates loaded"

            # Running again should not create duplicates.
            assert repository.load_dates() == 0

            # Load unique venues into the warehouse.
            inserted = repository.load_venues()

            # Verify that venues exist.
            venue_count = session.scalar(
                select(func.count()).select_from(DimVenue)
            )

            assert venue_count > 0, "No venues loaded"

            # Verify idempotency.
            assert repository.load_venues() == 0

            print(f"\nNew venues inserted: {inserted}")
            print(f"Total warehouse venues: {venue_count}")

            # Load categories into the warehouse.
            inserted = repository.load_categories()

            category_count = session.scalar(
                select(func.count()).select_from(DimCategory)
            )

            assert category_count > 0, "No categories loaded"

            # Running the loader again should insert nothing.
            assert repository.load_categories() == 0

            print(f"New categories inserted: {inserted}")
            print(f"Total warehouse categories: {category_count}")

            # Load event facts into the warehouse.
            inserted = repository.load_facts()

            fact_count = session.scalar(
                select(func.count()).select_from(FactEvent)
            )

            source_count = session.scalar(
                select(func.count()).select_from(Event)
            )

            assert fact_count == source_count, (
                f"Expected {source_count} facts, found {fact_count}"
            )

            # Verify idempotency.
            assert repository.load_facts() == 0

            print(f"New facts inserted: {inserted}")
            print(f"Total warehouse facts: {fact_count}")
    finally:
        engine.dispose()