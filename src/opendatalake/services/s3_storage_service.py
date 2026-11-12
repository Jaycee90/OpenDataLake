
import json
import logging
from datetime import datetime, timezone
from typing import Any

import boto3

logger = logging.getLogger(__name__)


class S3StorageService:
    def __init__(self, bucket_name: str, profile_name: str = "opendatalake"):
        self.bucket_name = bucket_name

        # boto3.Session authenticates using your existing AWS CLI profile.
        session = boto3.Session(
            profile_name=profile_name,
            region_name="us-east-1",
        )
        self.s3_client = session.client("s3")

    def upload_raw_events(self, events: list[dict[str, Any]]) -> str:
        """Upload raw Ticketmaster events as a JSON object."""

        timestamp = datetime.now(timezone.utc).strftime(
            "%Y/%m/%d/%H%M%S-%f"
        )

        object_key = f"raw/ticketmaster/{timestamp}.json"

        # json.dumps() converts the raw event dictionaries into JSON.
        json_data = json.dumps(events, ensure_ascii=False).encode("utf-8")

        # put_object() uploads the JSON data to S3 with metadata.
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=object_key,
            Body=json_data,
            ContentType="application/json",
            Metadata={
                "source": "ticketmaster",
                "pipeline": "opendatalake",
                "environment": "dev",
            },
        )

        logger.info(
            "Uploaded %d raw events to s3://%s/%s",
            len(events),
            self.bucket_name,
            object_key,
        )

        return object_key
