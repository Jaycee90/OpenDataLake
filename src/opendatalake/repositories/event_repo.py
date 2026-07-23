'''
The EventRepository is responsible for all persistence operations
for Event objects. It uses SQLAlchemy sessions to communicate with
the database while hiding database details from the rest of the
application.
'''
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, sessionmaker

from opendatalake.database.models.event import Event

class EventRepository:

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        # _session_factory tells other developers that this is an internal dependency. Don't access it outside this class."
        self._session_factory = session_factory

    def upsert_all(self, events: list[Event]) -> None:
        if not events:
            return

        rows = [
            {
                column.name: getattr(event, column.name)
                for column in Event.__table__.columns
                if column.name not in {
                    "id",
                    "created_at",
                    "updated_at",
                }
            }
            for event in events
        ]

        statement = insert(Event).values(rows)

        excluded_columns = {
            "id",
            "event_id",
            "created_at",
            "updated_at",
        }

        update_columns = {
            column.name: getattr(statement.excluded, column.name)
            for column in Event.__table__.columns
            if column.name not in excluded_columns
        }

        update_columns["updated_at"] = func.now()

        statement = statement.on_conflict_do_update(
            index_elements=[Event.event_id],
            set_=update_columns,
        )

        '''
        This is a transaction
        session.begin() does this:
        BEGIN
        → execute the upsert
        → COMMIT if successful
        → ROLLBACK if an exception occurs
        '''
        with self._session_factory() as session:
            with session.begin():
                session.execute(statement)