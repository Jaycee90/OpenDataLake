import pytest

from datetime import date, time
from tests.conftest import recipe
from tests.factories.event_factory import create_event
from unittest.mock import call
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
def test_load_calls_event_repository(recipe):
    events = [create_event()]

    recipe.load(events)

    recipe._event_repository.upsert_all.assert_called_once_with(events)

# Test whether after loading, did it refresh the materialized views?
def test_load_refreshes_analytics(recipe):
    events = [create_event()]

    recipe.load(events)

    recipe._analytics_repository.refresh_all.assert_called_once()

# Verifies whether every city is requested in order.
def test_extract_gets_events_for_all_cities(recipe):
    recipe._ticketmaster_service.get_events.return_value = []

    recipe.extract()

    expected_calls = [
        call(city=city, size=20)
        for city in recipe.CITIES
    ]

    assert recipe._ticketmaster_service.get_events.call_args_list == expected_calls
    # print(recipe._ticketmaster_service.get_events.call_args_list)

# Test that events are combined
def test_extract_combines_events_from_all_cities(recipe):
    recipe._ticketmaster_service.get_events.side_effect = [
        [{"id": "austin-1"}],
        [{"id": "new-york-1"}],
        [],
        [],
        [],
        [],
        [],
        [{"id": "seattle-1"}],
    ]

    result = recipe.extract()
    # print(result)
    expected = [{'id': 'austin-1', 'requested_city': 'Austin'}, {'id': 'new-york-1', 'requested_city': 'New York'}, {'id': 'seattle-1', 'requested_city': 'Seattle'}]

    assert result == expected
    # print(f"Expected: {expected} matches the result: {result}" )
    
    # You can test the combination this way too
    # assert result == [
    #     {
    #         "id": "austin-1",
    #         "requested_city": "Austin",
    #     },
    #     {
    #         "id": "new-york-1",
    #         "requested_city": "New York",
    #     },
    #     {
    #         "id": "seattle-1",
    #         "requested_city": "Seattle",
    #     },
    # ]

def test_extract_skips_city_when_ticketmaster_error_occurs(recipe):
    recipe._ticketmaster_service.get_events.side_effect = [
        TicketmasterError("API failed"),
        [{"id": "new-york-1"}],
        [],
        [],
        [],
        [],
        [],
        [],
    ]

    result = recipe.extract()

    assert result == [
        {
            "id": "new-york-1",
            "requested_city": "New York",
        }
    ]

# Test whether extract calls the API() for every city
def test_extract_calls_the_api_for_every_city(recipe):
    recipe._ticketmaster_service.get_events.return_value = []
    result = recipe.extract()

    # print(result)
    # print(recipe._ticketmaster_service.get_events.call_count)
    # print(recipe._ticketmaster_service.get_events.call_args_list)

    expected_calls = [call(city=city, size=20) for city in recipe.CITIES]
    assert recipe._ticketmaster_service.get_events.call_args_list == expected_calls