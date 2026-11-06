from datetime import datetime, timezone

import pytest

from opendatalake.utils.date_windows import split_date_window


def test_split_date_window():
    start = datetime(2026, 11, 1, tzinfo=timezone.utc)
    end = datetime(2026, 12, 1, tzinfo=timezone.utc)

    first, second = split_date_window(start, end)

    assert first[0] == start
    assert first[1] == second[0]
    assert second[1] == end

    assert first[0] < first[1]
    assert second[0] < second[1]


def test_split_date_window_rejects_invalid_range():
    start = datetime(2026, 12, 1, tzinfo=timezone.utc)
    end = datetime(2026, 11, 1, tzinfo=timezone.utc)

    with pytest.raises(ValueError, match="Window start must be before window end"):
        split_date_window(start, end)


def test_split_date_window_requires_timezone():
    start = datetime(2026, 11, 1)
    end = datetime(2026, 12, 1)

    with pytest.raises(ValueError, match="timezone-aware"):
        split_date_window(start, end)

def test_split_date_window_rejects_tiny_window():
    start = datetime(2026, 11, 1, tzinfo=timezone.utc)
    end = datetime(2026, 11, 1, 0, 0, 1, tzinfo=timezone.utc)

    with pytest.raises(
        ValueError,
        match="Date window is too small to split safely",
    ):
        split_date_window(start, end)

def test_split_date_window_uses_whole_seconds():
    start = datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
    end = datetime(2026, 11, 1, 0, 0, 5, tzinfo=timezone.utc)

    first, second = split_date_window(start, end)

    assert first[1] == datetime(
        2026, 11, 1, 0, 0, 2, tzinfo=timezone.utc
    )
    assert first[1] == second[0]
    assert first[1].microsecond == 0