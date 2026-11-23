import json
import logging
from datetime import datetime, timezone
from typing import Any
import os
import tempfile

import boto3

logger = logging.getLogger(__name__)


class S3StorageService:
    # Make S3 authentication work locally and on ECS
    # For local development, continue using your existing AWS_PROFILE=opendatalake setting.
    # For ECS, we'll leave AWS_PROFILE unset.
    def __init__(self, bucket_name: str, profile_name: str | None = None):
        self.bucket_name = bucket_name

        # Local: use the AWS profile when provided.
        # ECS: automatically use credentials from the IAM task role.
        session = boto3.Session(
            profile_name=profile_name,
            region_name="us-east-1",
        )

        self.s3_client = session.client("s3")

    def upload_raw_events(self, events: list[dict[str, Any]]) -> str:
        """Upload raw Ticketmaster events without serializing all JSON in memory."""

        timestamp = datetime.now(timezone.utc).strftime(
            "%Y/%m/%d/%H%M%S-%f"
        )

        object_key = f"raw/ticketmaster/{timestamp}.json"

        temp_path = None

        try:
            # Write JSON incrementally to disk instead of building
            # one enormous JSON string in memory.
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                suffix=".json",
                delete=False,
            ) as temp_file:
                temp_path = temp_file.name

                json.dump(events, temp_file, ensure_ascii=False)

            # boto3 streams the file to S3 rather than requiring
            # the entire JSON payload in memory.
            self.s3_client.upload_file(
                Filename=temp_path,
                Bucket=self.bucket_name,
                Key=object_key,
                ExtraArgs={
                    "ContentType": "application/json",
                    "Metadata": {
                        "source": "ticketmaster",
                        "pipeline": "opendatalake",
                        "environment": "dev",
                    },
                },
            )

            logger.info(
                "Uploaded %d raw events to s3://%s/%s",
                len(events),
                self.bucket_name,
                object_key,
            )

            return object_key

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)