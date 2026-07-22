'''
The responsability of the EventRepository is to answer this question: "How do I save Events?"
'''
from sqlalchemy.orm import Session, sessionmaker
from opendatalake.database.models.event import Event

class EventRepository:

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        # _session_factory tells other developers that this is an internal dependency. Don't access it outside this class."
        self._session_factory = session_factory

    def save_all(self, events: list[Event]) -> None:
        with self._session_factory() as session:
            with session.begin():
                session.add_all(events)