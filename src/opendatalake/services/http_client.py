import time
import logging
from typing import Any

import requests
from opendatalake.exceptions.http_client_error import HttpClientError

logger = logging.getLogger(__name__)

class HttpClient:
    RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

    def get_json(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        timeout: float = 10.0,
        max_attempts: int = 3,
        delay: float = 1.0,
    ) -> dict[str, Any]:

        """Send an HTTP GET request and return the JSON response.

        Example query parameters:

            {
                "city": "Austin",
                "apikey": "secret",
            }

        Conceptually becomes:

            https://example.com?city=Austin&apikey=secret
        """

        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        if delay < 0:
            raise ValueError("delay cannot be negative")
        
        for attempt in range(max_attempts):
            try:
                logger.info("HTTP GET attempt %d/%d: %s", attempt + 1, max_attempts, url)
                logger.debug("Sending GET request to %s with params: %s", url, params)

                response = requests.get(url, params=params, timeout=timeout,)

                # raises an exception for unsuccessful HTTP responses before we try to treat the response as valid data.
                response.raise_for_status()

                return response.json() # converts the JSON response into Python dictionaries and lists.
            
            except requests.Timeout as e:
                if attempt == max_attempts - 1:
                    raise HttpClientError(f"Request to {url} timed out after {max_attempts} attempts.") from e
                self._wait_before_retry(attempt=attempt, delay=delay, reason="request timed out")

            except requests.ConnectionError as e:
                if attempt == max_attempts - 1:
                    raise HttpClientError(f"Connection error occurred while trying to reach {url}.") from e
                self._wait_before_retry(attempt=attempt, delay=delay, reason="connection error")
            
            except requests.HTTPError as e:
                status_code = e.response.status_code if e.response is not None else "unknown"
                if status_code not in self.RETRYABLE_STATUS_CODES:
                    raise HttpClientError(f"HTTP error {status_code} occurred while trying to reach {url}.") from e
                if attempt == max_attempts - 1:
                    raise HttpClientError(f"HTTP error {status_code} occurred while trying to reach {url}.") from e
                self._wait_before_retry(attempt=attempt, delay=delay, reason=f"HTTP error {status_code}")

            except requests.exceptions.JSONDecodeError as e:
                raise HttpClientError("Remote service returned invalid JSON") from e

            except requests.RequestException as e:
                raise HttpClientError("Unexpected HTTP request failure") from e
            
    @staticmethod
    def _wait_before_retry(attempt: int, delay: float, reason: str) -> None:
        wait_time = delay * (2**attempt)  # Exponential backoff
        logger.warning("Attempt %d failed due to %s. Retrying in %.2f seconds...", attempt + 1, reason, wait_time,)
        time.sleep(wait_time)