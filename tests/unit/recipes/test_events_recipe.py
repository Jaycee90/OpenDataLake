import pytest

from datetime import date, time
from tests.conftest import recipe
from tests.factories.event_factory import create_event
from unittest.mock import Mock, call, patch
from opendatalake.exceptions.ticketmaster_error import TicketmasterError

def test_validate_raises_error_when_events_are_empty(recipe):
    
    with pytest.raises(ValueError, match="No events were returned"):
        recipe.validate([])

def test_validate_raises_error_when_event_id_is_missing(recipe):

    event = create_event(event_id=None)

    with pytest.raises(ValueError, match="Event ID cannot be empty"):
        recipe.validate([event])

def test_validate_raises_error_when_name_is_missing(recipe):

    event = create_event(name=None)

    with pytest.raises(ValueError, match="Event event-123 has no name",):
        recipe.validate([event])

def test_validate_raises_error_when_city_is_missing(recipe):

    event = create_event(city=None)

    with pytest.raises(ValueError, match="Event event-123 has no city",):
        recipe.validate([event])

def test_validate_raises_error_when_event_date_is_missing(recipe):

    event = create_event(event_date=None)

    with pytest.raises(ValueError, match="Event event-123 has no date",):
        recipe.validate([event])

def test_validate_raises_error_when_duplicate_event_detected(recipe):

    event1 = create_event(event_id="123")
    event2 = create_event(event_id="123")

    with pytest.raises(ValueError, match="Duplicate event ID: 123",):
        recipe.validate([event1, event2])

def test_validate_passes_when_event_is_valid(recipe):

    event = create_event()

    recipe.validate([event])


def test_transform_maps_raw_event_to_event_model(recipe):
    raw_data = [
        {
            "id": "event-123",
            "requested_city": "Austin",
            "requested_state": "TX",
            "name": "Austin Music Festival",
            "url": "https://example.com/event-123",
            "dates": {
                "start": {
                    "localDate": "2026-07-24",
                    "localTime": "19:30:00",
                },
                "status": {
                    "code": "onsale",
                },
            },
            "classifications": [
                {
                    "segment": {"name": "Music"},
                    "genre": {"name": "Rock"},
                    "subGenre": {"name": "Alternative Rock"},
                }
            ],
            "_embedded": {
                "venues": [
                    {
                        "name": "Austin Arena",
                        "city": {"name": "Austin"},
                        "state": {"stateCode": "TX"},
                        "address": {"line1": "100 Main Street"},
                        "location": {
                            "latitude": "30.2672",
                            "longitude": "-97.7431",
                        },
                    }
                ]
            },
        }
    ]

    result = recipe.transform(raw_data)

    assert len(result) == 1

    event = result[0]

    assert event.event_id == "event-123"
    assert event.name == "Austin Music Festival"
    assert event.event_url == "https://example.com/event-123"
    assert event.event_date == date(2026, 7, 24)
    assert event.event_time == time(19, 30)
    assert event.status == "onsale"
    assert event.category == "Music"
    assert event.genre == "Rock"
    assert event.subgenre == "Alternative Rock"
    assert event.venue == "Austin Arena"
    assert event.city == "Austin"
    assert event.state == "TX"
    assert event.address == "100 Main Street"
    assert event.latitude == "30.2672"
    assert event.longitude == "-97.7431"
    assert event.source == "ticketmaster"

# Test whether load() tell the repository to save these events?"
@patch("opendatalake.recipes.events.WarehouseRepository")
def test_load_calls_event_repository(mock_warehouse, recipe):
    events = [create_event()]

    recipe.load(events)

    session = recipe._session_factory.begin.return_value.__enter__.return_value

    recipe._event_repository.upsert_all.assert_called_once_with(
        events,
        session=session,
    )

    mock_warehouse.assert_called_once_with(session)

# Test whether after loading, did it refresh the materialized views?
@patch("opendatalake.recipes.events.WarehouseRepository")
def test_load_refreshes_analytics(mock_warehouse, recipe):
    events = [create_event()]

    recipe.load(events)

    session = recipe._session_factory.begin.return_value.__enter__.return_value

    recipe._analytics_repository.refresh_all.assert_called_once_with(
        session=session,
    )

# The @patch decorator replaces the real WarehouseRepository with a mock,
# so this test doesn't insert anything into PostgreSQL or call Ticketmaster.
@patch("opendatalake.recipes.events.WarehouseRepository")
def test_load_facts_only_for_current_batch(mock_warehouse, recipe):
    events = [
        create_event(event_id="event-1"),
        create_event(event_id="event-2"),
    ]

    recipe.load(events)

    warehouse = mock_warehouse.return_value

    warehouse.load_dates.assert_called_once_with(
        event_ids=["event-1", "event-2"]
    )

    warehouse.load_venues.assert_called_once_with(
        event_ids=["event-1", "event-2"]
    )

    warehouse.load_categories.assert_called_once_with(
        event_ids=["event-1", "event-2"]
    )

    warehouse.load_facts.assert_called_once_with(
        event_ids=["event-1", "event-2"]
    )

# Verifies whether every city is requested in order.
def test_extract_gets_events_for_all_cities(recipe):
    recipe._extract_window = Mock(return_value=[])

    recipe.extract()

    actual_calls = recipe._extract_window.call_args_list

    assert len(actual_calls) == len(recipe.CITIES)

    assert [
        (c.kwargs["city"], c.kwargs["state"])
        for c in actual_calls
    ] == recipe.CITIES

# Test that events are combined
def test_extract_combines_events_from_all_cities(recipe):
    responses = {
        "Austin": [{"id": "austin-1"}],
        "New York": [{"id": "new-york-1"}],
        "Seattle": [{"id": "seattle-1"}],
    }

    def fake_extract_window(city, state, start, end):
        return responses.get(city, [])

    recipe._extract_window = Mock(side_effect=fake_extract_window)

    result = recipe.extract()

    assert result == [
    {"id": "new-york-1", "requested_city": "New York", "requested_state": "NY"},
    {"id": "austin-1", "requested_city": "Austin", "requested_state": "TX"},
    {"id": "seattle-1", "requested_city": "Seattle", "requested_state": "WA"},
    ]

def test_extract_raises_when_ticketmaster_error_occurs(recipe):
    recipe._extract_window = Mock(
        side_effect=TicketmasterError("API failed")
    )

    with pytest.raises(TicketmasterError, match="API failed"):
        recipe.extract()

# Test whether extract calls the API() for every city
def test_extract_calls_the_api_for_every_city(recipe):
    recipe._extract_window = Mock(return_value=[])
    result = recipe.extract()

    # print(result)
    # print(recipe._ticketmaster_service.get_events.call_count)
    # print(recipe._ticketmaster_service.get_events.call_args_list)

    actual_calls = recipe._extract_window.call_args_list

    assert len(actual_calls) == len(recipe.CITIES)

    assert [
        (c.kwargs["city"], c.kwargs["state"])
        for c in actual_calls
    ] == recipe.CITIES

def test_transform_removes_city_whitespace(recipe):
    raw_data = [
        {
            "id": "event-456",
            "requested_city": "Miami",
            "requested_state": "FL",
            "name": "Miami Concert",
            "dates": {
                "start": {"localDate": "2026-11-10"}
            },
            "_embedded": {
                "venues": [
                    {
                        "city": {"name": " Miami "},
                        "state": {"stateCode": " FL "}
                    }
                ]
            }
        }
    ]

    result = recipe.transform(raw_data)

    assert result[0].city == "Miami"
    assert result[0].state == "FL"

def test_transform_skips_events_from_wrong_state(recipe):
    raw_data = [
        {
            "id": "event-789",
            "name": "Nashville Concert",
            "requested_city": "Nashville",
            "requested_state": "TN",
            "dates": {
                "start": {
                    "localDate": "2026-12-15"
                }
            },
            "_embedded": {
                "venues": [
                    {
                        "name": "Brown County Music Center",
                        "city": {"name": "Nashville"},
                        "state": {"stateCode": "IN"},
                    }
                ]
            },
        }
    ]

    result = recipe.transform(raw_data)

    assert result == []

def test_extract_window_fetches_all_pages(recipe):
    from datetime import datetime, timezone
    from unittest.mock import Mock

    start = datetime(2026, 11, 1, tzinfo=timezone.utc)
    end = datetime(2026, 12, 1, tzinfo=timezone.utc)

    recipe._ticketmaster_service.get_event_page = Mock(
        side_effect=[
            {
                "page": {"totalPages": 3, "totalElements": 3},
                "_embedded": {"events": [{"id": "event-1"}]},
            },
            {
                "page": {"totalPages": 3, "totalElements": 3},
                "_embedded": {"events": [{"id": "event-2"}]},
            },
            {
                "page": {"totalPages": 3, "totalElements": 3},
                "_embedded": {"events": [{"id": "event-3"}]},
            },
        ]
    )

    events = recipe._extract_window(
        city="Austin",
        state="TX",
        start=start,
        end=end,
    )

    assert len(events) == 3
    assert [event["id"] for event in events] == [
        "event-1",
        "event-2",
        "event-3",
    ]

    assert recipe._ticketmaster_service.get_event_page.call_count == 3

    requested_pages = [
        call.kwargs["page"]
        for call in recipe._ticketmaster_service.get_event_page.call_args_list
    ]

    assert requested_pages == [0, 1, 2]

def test_extract_window_splits_when_page_limit_exceeded(recipe):
    from datetime import datetime, timezone
    from unittest.mock import Mock

    start = datetime(2026, 11, 1, tzinfo=timezone.utc)
    end = datetime(2026, 12, 1, tzinfo=timezone.utc)

    recipe._ticketmaster_service.get_event_page = Mock(
        side_effect=[
            {
                # Parent window: too many pages, so split
                "page": {"totalPages": 74, "totalElements": 3700},
                "_embedded": {"events": [{"id": "ignored-parent"}]},
            },
            {
                # First half: one event
                "page": {"totalPages": 1, "totalElements": 1},
                "_embedded": {"events": [{"id": "event-first-half"}]},
            },
            {
                # Second half: one event
                "page": {"totalPages": 1, "totalElements": 1},
                "_embedded": {"events": [{"id": "event-second-half"}]},
            },
        ]
    )

    events = recipe._extract_window(
        city="Las Vegas",
        state="NV",
        start=start,
        end=end,
    )

    assert [event["id"] for event in events] == [
        "event-first-half",
        "event-second-half",
    ]

    assert recipe._ticketmaster_service.get_event_page.call_count == 3

    calls = recipe._ticketmaster_service.get_event_page.call_args_list

    midpoint = datetime(2026, 11, 16, tzinfo=timezone.utc)

    assert calls[0].kwargs["start_date_time"] == "2026-11-01T00:00:00Z"
    assert calls[0].kwargs["end_date_time"] == "2026-11-30T23:59:59Z"

    assert calls[1].kwargs["start_date_time"] == "2026-11-01T00:00:00Z"
    assert calls[1].kwargs["end_date_time"] == "2026-11-15T23:59:59Z"

    assert calls[2].kwargs["start_date_time"] == "2026-11-16T00:00:00Z"
    assert calls[2].kwargs["end_date_time"] == "2026-11-30T23:59:59Z"

def test_deduplicate_events(recipe):
    events = [
        {"id": "event-1"},
        {"id": "event-2"},
        {"id": "event-1"},
        {"id": "event-3"},
        {"id": "event-2"},
    ]

    result = recipe._deduplicate_events(events)

    assert [event["id"] for event in result] == [
        "event-1",
        "event-2",
        "event-3",
    ]

def test_extract_window_rejects_non_utc_timestamps(recipe):
    from datetime import datetime, timezone, timedelta
    import pytest

    central_time = timezone(timedelta(hours=-6))

    start = datetime(
        2026, 11, 1, 0, 0, tzinfo=central_time
    )
    end = datetime(
        2026, 12, 1, 0, 0, tzinfo=central_time
    )

    with pytest.raises(
        ValueError,
        match="Extraction windows must use UTC timestamps",
    ):
        recipe._extract_window(
            city="Austin",
            state="TX",
            start=start,
            end=end,
        )

    recipe._ticketmaster_service.get_event_page.assert_not_called()