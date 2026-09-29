'''
A factory creates domain objects (the data you're testing).
Factories answer: "How do I create a valid object?"
'''

from datetime import date, time

from opendatalake.database.models.event import Event


def create_event(**overrides):
    defaults = {
        "event_id": "event-123",
        "name": "Austin Concert",
        "event_url": "https://ticketmaster.com/event/123",
        "event_date": date.today(),
        "event_time": time(19, 30),
        "status": "onsale",
        "category": "Music",
        "genre": "Rock",
        "subgenre": "Alternative",
        "venue": "Moody Center",
        "city": "Austin",
        "state": "TX",
        "address": "2001 Robert Dedman Dr",
        "latitude": 30.2807,
        "longitude": -97.7325,
        "source": "ticketmaster",
    }

    defaults.update(overrides)

    return Event(**defaults)