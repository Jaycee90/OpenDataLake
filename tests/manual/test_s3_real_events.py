# This script fetches real events from the Ticketmaster API and uploads them to an S3 bucket.
# It is intended for manual testing and demonstration purposes only.
# It runs on-demand and is not part of the automated pipeline.
from opendatalake.config.settings import Settings
from opendatalake.services.http_client import HttpClient
from opendatalake.services.ticketmaster_service import TicketmasterService
from opendatalake.services.s3_storage_service import S3StorageService


def main():
    settings = Settings.load()

    ticketmaster = TicketmasterService(
        http_client=HttpClient(),
        settings=settings,
    )

    # Fetch only 5 real events from Austin, Texas.
    events = ticketmaster.get_events(
        city="Austin",
        state="TX",
        size=5,
    )

    print(f"Fetched {len(events)} real events")

    if not events:
        print("No events found. Nothing uploaded.")
        return

    s3 = S3StorageService(
        bucket_name="opendatalake-raw-8f2445ce62ec6513bb05805ece",
    )

    object_key = s3.upload_raw_events(events)

    print("Successfully uploaded to S3!")
    print(f"Object key: {object_key}")


if __name__ == "__main__":
    main()
