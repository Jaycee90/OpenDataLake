import argparse

from opendatalake.config.settings import Settings
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

    settings = Settings.load()  # Load settings from environment variables
    http_client = HttpClient()
    ticketmaster_service = TicketmasterService(http_client=http_client, settings=settings)
    events_recipe = EventsRecipe(ticketmaster_service)

    registry = RecipeRegistry()
    registry.register(events_recipe) # Registers recipe

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