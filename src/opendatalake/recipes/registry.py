from opendatalake.recipes.base import BaseRecipe


class RecipeRegistry:
    def __init__(self) -> None:
        # self.recipes is a dictionary where the keys are strings and the values are BaseRecipe-compatible objects.
        self.recipes: dict[str, BaseRecipe] = {}

    def register(self, recipe: BaseRecipe) -> None:
        # Suppose we call: registry.register(AustinEventsRecipe())
        #Inside register(): recipe refers to the AustinEventsRecipe object. Then: recipe.name is: "austin_events"
        self.recipes[recipe.name] = recipe

    def get_recipe(self, name: str) -> BaseRecipe:
        if name not in self.recipes:
            available = ", ".join(self.recipes.keys())
            raise ValueError(
                f"Recipe '{name}' was not found.\n"
                f"Available recipes: {available}"
            )

        return self.recipes[name]

    def get_all(self) -> list[BaseRecipe]:
        return list(self.recipes.values())