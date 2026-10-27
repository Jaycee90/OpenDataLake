from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

'''
Handles PostgreSQL analytics objects derived from events:

refresh event materialized views
read event analytics results, when needed
run event-specific analytical database queries
'''

class AnalyticsRepository:

    MATERIALIZED_VIEWS = (
        "top_categories_by_city",
        "event_counts_by_city_and_month",
    )

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
    

    def refresh_all(self, session: Session | None = None) -> None:
        if session is not None:
            for view_name in self.MATERIALIZED_VIEWS:
                session.execute(
                    text(f"REFRESH MATERIALIZED VIEW analytics.{view_name}")
                )
        else:
            with self._session_factory.begin() as own_session:
                for view_name in self.MATERIALIZED_VIEWS:
                    own_session.execute(
                        text(f"REFRESH MATERIALIZED VIEW analytics.{view_name}")
                    )