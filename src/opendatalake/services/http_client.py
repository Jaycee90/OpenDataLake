from typing import Any

import requests


class HttpClient:
    def get_json(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        timeout: float = 10.0,
    ) -> dict[str, Any]:
        ''' Send an HTTP GET request to the specified URL with optional query parameters and a timeout.
        example usage:
            {
                "city": "Austin",
                "apikey": "secret",
            }
        becomes conceptually: https://example.com?city=Austin&apikey=secret
        '''
        response = requests.get(
            url,
            params=params,
            timeout=timeout,
        )

        # raises an exception for unsuccessful HTTP responses before we try to treat the response as valid data.
        response.raise_for_status()

        return response.json() # converts the JSON response into Python dictionaries and lists.