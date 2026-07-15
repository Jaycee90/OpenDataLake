from opendatalake.recipes.registry import RecipeRegistry


class Runner:
    def __init__(self, registry: RecipeRegistry) -> None:
        self.registry = registry

    def start(self) -> None:
        print("Starting OpenDataLake...")

        for recipe in self.registry.get_all():
            recipe.run()

        print("Done.")