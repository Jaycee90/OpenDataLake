import logging
from opendatalake.recipes.base import BaseRecipe
from opendatalake.recipes.registry import RecipeRegistry

logger = logging.getLogger(__name__)

class Runner:
    def __init__(self, registry: RecipeRegistry) -> None:
        self.registry = registry

    def run_all(self) -> None:
        logger.info("Starting OpenDataLake...")
        
        for recipe in self.registry.get_all():
            recipe.run()

        logger.info("OpenDataLake execution completed.")
    def run_recipe(self, recipe_name: str) -> None:
        logger.info(f"Starting recipe: {recipe_name}")

        recipe: BaseRecipe = self.registry.get_recipe(recipe_name)
        recipe.run()

        logger.info("Recipe execution completed.")