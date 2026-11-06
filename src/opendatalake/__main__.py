import argparse
from sqlalchemy import text

from opendatalake.database.database_session import create_database_engine, create_database_tables, create_session_factory
from opendatalake.config.settings import Settings
from opendatalake.repositories.event_repo import EventRepository
from opendatalake.repositories.analytics_repo import AnalyticsRepository
from opendatalake.services.http_client import HttpClient
from opendatalake.services.ticketmaster_service import TicketmasterService
from opendatalake.recipes.events import EventsRecipe
from opendatalake.recipes.registry import RecipeRegistry
from opendatalake.runner import Runner
from opendatalake.config.logger import configure_logging

'''The bootstrap creates and connects the objects:

    RecipeRegistry()
    AustinEventsRecipe()
    Runner(registry)
This is called wiring dependencies or dependency injection.
The Runner needs a registry, so the bootstrap injects one:
    runner = Runner(registry)
Runner does not create its own dependency.
'''

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run OpenDataLake ETL recipes."
    )

    parser.add_argument(
        "--recipe",
        type=str,
        help="Run one recipe by name.",
    )

    return parser.parse_args()

def main() -> None:
    configure_logging()  # Configure logging at the start of the application
    arguments = parse_arguments()

    # 1. Settings.load()
    # Reads environment configuration, including the PostgreSQL URL and Ticketmaster settings
    settings = Settings.load()


    #2. create_database_engine(settings)
    # Configures PostgreSQL connectivity
    engine = create_database_engine(settings)

    #3. create_database_tables(engine)
    # Creates missing registered tables
    create_database_tables(engine)  # Create database tables if they don't exist


    # 4. create_session_factory(engine)
    # Prepares database sessions for repositories
    session_factory = create_session_factory(engine)
    with engine.connect() as connection:
        database_name = connection.execute(
            text("SELECT current_database()")
        ).scalar_one()
        print(f"Connected to: {database_name}")


    # 5. Dependency injection
    # Builds HTTP client, Ticketmaster service, repositories, and recipe
    http_client = HttpClient()

    ticketmaster_service = TicketmasterService(http_client=http_client, settings=settings)
    event_repository = EventRepository(session_factory=session_factory)
    analytics_repository = AnalyticsRepository(session_factory=session_factory)
    events_recipe = EventsRecipe(ticketmaster_service=ticketmaster_service, event_repository=event_repository, analytics_repository=analytics_repository, session_factory=session_factory)
    registry = RecipeRegistry()
    registry.register(events_recipe) # Registers recipe


    # 6. runner.run_all() or runner.run_recipe()
    # Executes your ETL pipeline
    runner = Runner(registry) # injects the registry dependency into the Runner

    try:
        if arguments.recipe:
            runner.run_recipe(arguments.recipe)
        else:
            runner.run_all()

    except ValueError as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    main()