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