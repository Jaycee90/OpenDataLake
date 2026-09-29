'''
A fixture creates the test environment.
Example:

@pytest.fixture
def recipe():
    return EventsRecipe(...)

It creates the object you're testing.
Fixtures answer:"What setup does every test need?"
'''


import pytest
from unittest.mock import Mock

from opendatalake.recipes.events import EventsRecipe


@pytest.fixture
def recipe():
    return EventsRecipe(
        ticketmaster_service=Mock(),
        event_repository=Mock(),
        analytics_repository=Mock(),
    )