from datetime import datetime, timedelta, timezone


def split_date_window(
    start: datetime,
    end: datetime,
) -> tuple[tuple[datetime, datetime], tuple[datetime, datetime]]:
    """Split a date window into two non-overlapping halves."""

    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("Date windows must be timezone-aware")

    if start >= end:
        raise ValueError("Window start must be before window end")

    if end - start < timedelta(seconds=2):
        raise ValueError("Date window is too small to split safely")

    midpoint = (start + (end - start) / 2).replace(microsecond=0)

    if midpoint <= start or midpoint >= end:
        raise ValueError("Date window is too small to split")

    return (
        (start, midpoint),
        (midpoint, end),
    )