from abc import ABC, abstractmethod


class BaseRecipe(ABC):
    name: str = "base"

    def run(self) -> None:
        print(f"Running recipe: {self.name}")
        raw_data = self.extract()
        transformed_data = self.transform(raw_data)
        self.load(transformed_data)
        print(f"Finished recipe: {self.name}")

    @abstractmethod
    def extract(self):
        pass

    @abstractmethod
    def transform(self, raw_data):
        pass

    @abstractmethod
    def load(self, transformed_data) -> None:
        pass