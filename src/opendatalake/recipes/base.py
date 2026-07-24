from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class BaseRecipe(ABC):
    name: str = "base"

    def run(self) -> None:
        logger.info(f"Running recipe: {self.name}")

        raw_data = self.extract()
        transformed_data = self.transform(raw_data)
        self.validate(transformed_data)
        self.load(transformed_data)
        logger.info(f"Finished recipe: {self.name}")

    @abstractmethod
    def extract(self):
        pass

    @abstractmethod
    def transform(self, raw_data):
        pass

    @abstractmethod
    def validate(self, transformed_data) -> None:
        pass

    @abstractmethod
    def load(self, transformed_data) -> None:
        pass