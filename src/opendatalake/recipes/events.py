from typing import Any

from opendatalake.recipes.base import BaseRecipe


class AustinEventsRecipe(BaseRecipe):
    name = "austin_events"

    def extract(self) -> Any:
        print("Extracting Austin events...")
        return [
            {
                "event_name": "Austin City Limits Live",
                "venue": "Moody Theater",
                "date": "2026-07-12",
                "category": "Music",
            },
            {
                "event_name": "Austin FC Match",
                "venue": "Q2 Stadium",
                "date": "2026-07-13",
                "category": "Sports",
            },
        ]

    def transform(self, raw_data: Any) -> Any:
        print("Transforming Austin events...")

        transformed = []

        for item in raw_data:
            transformed.append(
                {
                    "name": item["event_name"],
                    "venue": item["venue"],
                    "event_date": item["date"],
                    "category": item["category"],
                    "city": "Austin",
                    "source": "mock_data",
                }
            )

        return transformed

    def load(self, transformed_data: Any) -> None:
        print("Loading Austin events...")

        for item in transformed_data:
            print(item)