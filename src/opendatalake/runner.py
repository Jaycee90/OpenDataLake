from opendatalake.recipes.base import BaseRecipe
from opendatalake.recipes.registry import RecipeRegistry


class Runner:
    def __init__(self, registry: RecipeRegistry) -> None:
        self.registry = registry

    def run_all(self) -> None:
        print("Starting OpenDataLake...")

        for recipe in self.registry.get_all():
            recipe.run()

        print("Done.")

    def run_recipe(self, recipe_name: str) -> None:
        print(f"Starting recipe: {recipe_name}")

        recipe: BaseRecipe = self.registry.get_recipe(recipe_name)
        recipe.run()

        print("Done.")