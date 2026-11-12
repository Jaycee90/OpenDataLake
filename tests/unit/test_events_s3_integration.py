from unittest.mock import Mock

from opendatalake.recipes.events import EventsRecipe


def test_events_recipe_saves_raw_data_to_s3():
    raw_events = [
        {"id": "event-1", "name": "Austin Concert"}
    ]

    s3_storage = Mock()
    s3_storage.upload_raw_events.return_value = (
        "raw/ticketmaster/test.json"
    )

    recipe = EventsRecipe(
        ticketmaster_service=Mock(),
        event_repository=Mock(),
        analytics_repository=Mock(),
        session_factory=Mock(),
        s3_storage_service=s3_storage,
    )

    recipe.extract = Mock(return_value=raw_events)
    recipe.transform = Mock(return_value=[])
    recipe.validate = Mock()
    recipe.load = Mock()

    recipe.run()

    s3_storage.upload_raw_events.assert_called_once_with(raw_events)
    recipe.load.assert_called_once()