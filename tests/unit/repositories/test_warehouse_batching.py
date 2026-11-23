from opendatalake.database.repositories.warehouse_repository import (
    BATCH_SIZE,
    batch_event_ids,
)


def test_batch_event_ids():
    # Create more IDs than fit into two batches.
    event_ids = [str(i) for i in range(2500)]

    batches = list(batch_event_ids(event_ids))

    assert len(batches) == 3
    assert len(batches[0]) == BATCH_SIZE
    assert len(batches[1]) == BATCH_SIZE
    assert len(batches[2]) == 500

    # Verify that no IDs were lost or reordered.
    assert [event_id for batch in batches for event_id in batch] == event_ids

from unittest.mock import MagicMock, patch

from opendatalake.database.repositories.warehouse_repository import (
    WarehouseRepository,
)


def test_load_facts_queries_events_in_batches():
    session = MagicMock()

    # Simulate 2,500 event IDs.
    event_ids = [str(i) for i in range(2500)]

    # No event records returned by the mocked database.
    session.scalars.return_value.all.return_value = []

    # No venue/category dimension records.
    session.execute.return_value.all.return_value = []

    repository = WarehouseRepository(session)

    with patch(
        "opendatalake.database.repositories.warehouse_repository.BATCH_SIZE",
        1000,
    ):
        repository.load_facts(event_ids=event_ids)

    # Three event batches of 1,000, 1,000, and 500.
    assert session.scalars.call_count == 3

def test_load_facts_processes_each_batch_before_fetching_next():
    session = MagicMock()
    event_ids = [str(i) for i in range(1500)]

    first_batch = MagicMock()
    first_batch.event_id = "event-1"
    first_batch.event_date = None

    second_batch = MagicMock()
    second_batch.event_id = "event-2"
    second_batch.event_date = None

    processed_first_batch = False
    original_logger = (
        "opendatalake.database.repositories.warehouse_repository.logger"
    )

    def mock_scalars(query):
        nonlocal processed_first_batch

        result = MagicMock()

        # First call retrieves existing FactEvent records.
        if session.scalars.call_count == 1:
            result.all.return_value = []

        # Second call retrieves the first batch of Event records.
        elif session.scalars.call_count == 2:
            result.all.return_value = [first_batch]

        # Third call retrieves the second batch.
        elif session.scalars.call_count == 3:
            assert processed_first_batch, (
                "First batch was not processed before fetching the second"
            )
            result.all.return_value = [second_batch]

        else:
            result.all.return_value = []

        return result

    def mock_warning(*args, **kwargs):
        nonlocal processed_first_batch
        processed_first_batch = True

    session.scalars.side_effect = mock_scalars
    session.execute.return_value.all.return_value = []

    with patch(original_logger) as mock_logger:
        mock_logger.warning.side_effect = mock_warning

        repository = WarehouseRepository(session)
        repository.load_facts(event_ids=event_ids)

def test_load_venues_processes_each_batch_before_fetching_next():
    session = MagicMock()
    event_ids = [str(i) for i in range(1500)]

    first_venue = MagicMock()
    first_venue.venue = "Austin Arena"
    first_venue.city = "Austin"
    first_venue.state = "TX"

    second_venue = MagicMock()
    second_venue.venue = "Atlanta Arena"
    second_venue.city = "Atlanta"
    second_venue.state = "GA"

    first_batch_processed = False
    query_count = 0

    def mock_execute(query):
        nonlocal first_batch_processed, query_count

        query_count += 1
        result = MagicMock()

        if query_count == 1:
            result.all.return_value = [first_venue]

        elif query_count == 2:
            assert first_batch_processed, (
                "First venue batch was not processed before fetching the second"
            )
            result.all.return_value = [second_venue]

        else:
            result.all.return_value = []

        return result

    def mock_scalar(query):
        nonlocal first_batch_processed
        first_batch_processed = True
        return None

    session.execute.side_effect = mock_execute
    session.scalar.side_effect = mock_scalar

    repository = WarehouseRepository(session)
    inserted = repository.load_venues(event_ids=event_ids)

    assert inserted == 2
    assert query_count == 2
    assert session.add.call_count == 2

def test_load_facts_flushes_periodically():
    from datetime import date

    session = MagicMock()

    events = []

    for i in range(1200):
        event = MagicMock()
        event.event_id = f"event-{i}"
        event.event_date = date(2027, 1, 15)
        event.venue = "Test Arena"
        event.city = "Austin"
        event.state = "TX"
        event.category = "Music"
        event.genre = "Rock"
        event.subgenre = "Alternative"
        event.name = f"Concert {i}"
        event.status = "scheduled"
        events.append(event)

    from sqlalchemy.sql import Select
    from opendatalake.database.models.event import Event
    from opendatalake.database.models.fact_events import FactEvent

    event_batch_number = 0

    def mock_scalars(query):
        nonlocal event_batch_number

        result = MagicMock()

        if isinstance(query, Select):
            entities = {
                description.get("entity")
                for description in query.column_descriptions
            }

            if FactEvent in entities:
                result.all.return_value = []

            elif Event in entities:
                event_batch_number += 1

                if event_batch_number == 1:
                    result.all.return_value = events[:1000]
                elif event_batch_number == 2:
                    result.all.return_value = events[1000:]
                else:
                    result.all.return_value = []

            else:
                result.all.return_value = []

        return result

    session.scalars.side_effect = mock_scalars

    # Supply venue and category lookup records.
    venue = MagicMock()
    venue.venue_name = "Test Arena"
    venue.city = "Austin"
    venue.state = "TX"
    venue.venue_key = 1

    category = MagicMock()
    category.category = "Music"
    category.genre = "Rock"
    category.subgenre = "Alternative"
    category.category_key = 1

    session.execute.side_effect = [
        MagicMock(all=MagicMock(return_value=[venue])),
        MagicMock(all=MagicMock(return_value=[category])),
    ]

    repository = WarehouseRepository(session)

    inserted = repository.load_facts(
        event_ids=[event.event_id for event in events]
    )

    assert inserted == 1200
    assert session.add.call_count == 1200

    # One flush at 1,000 inserts, another for the remainder.
    assert session.flush.call_count == 2

    # The repository must not commit the caller's transaction.
    session.commit.assert_not_called()