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
def main() -> None:
    registry = RecipeRegistry()
    registry.register(AustinEventsRecipe()) # Registers recipe
    #registry.register(StockRecipe())

    runner = Runner(registry) # injects the registry dependency into the Runner
    runner.start()


if __name__ == "__main__":
    main()