from abc import ABC, abstractmethod
import logging
from time import perf_counter

logger = logging.getLogger(__name__)


class BaseRecipe(ABC):
    name: str = "base"

    def run(self) -> None:
        logger.info("Starting recipe: %s", self.name)
        start_time = perf_counter()

        try:
            raw_data = self.extract()
            transformed_data = self.transform(raw_data)
            self.validate(transformed_data)
            self.load(transformed_data)

        except Exception:
            logger.exception("Recipe failed: %s", self.name)
            raise

        finally:
            duration = perf_counter() - start_time
            logger.info(
                "Recipe %s execution time: %.2f seconds",
                self.name,
                duration,
            )

        logger.info("Recipe completed successfully: %s", self.name)

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