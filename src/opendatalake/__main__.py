import argparse

from opendatalake.recipes.events import AustinEventsRecipe
# from opendatalake.recipes.stocks import StockRecipe
from opendatalake.recipes.registry import RecipeRegistry
from opendatalake.runner import Runner

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
    arguments = parse_arguments()

    registry = RecipeRegistry()
    registry.register(AustinEventsRecipe()) # Registers recipe
    #registry.register(StockRecipe())

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