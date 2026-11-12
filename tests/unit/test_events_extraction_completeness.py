# This test verify that an incomplete Ticketmaster response causes the ETL to fail.
# it runs on demand and can de deleted after the ETL is fixed to handle incomplete responses gracefully.
from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from opendatalake.recipes.events import EventsRecipe


def test_incomplete_extraction_raises_error():
    # Arrange: Ticketmaster reports 10 events,
    # but the response contains only 5.
    ticketmaster_service = Mock()

    ticketmaster_service.get_event_page.return_value = {
        "page": {
            "totalPages": 1,
            "totalElements": 10,
        },
        "_embedded": {
            "events": [
                {"id": f"event-{i}"}
                for i in range(5)
            ]
        },
    }

    recipe = EventsRecipe(
        ticketmaster_service=ticketmaster_service,
        event_repository=Mock(),
        analytics_repository=Mock(),
        session_factory=Mock(),
    )

    start = datetime(2026, 11, 12, tzinfo=timezone.utc)
    end = datetime(2026, 11, 13, tzinfo=timezone.utc)

    # Act and assert: incomplete extraction must fail.
    with pytest.raises(ValueError, match="Incomplete extraction"):
        recipe._extract_window(
            city="Austin",
            state="TX",
            start=start,
            end=end,
        )