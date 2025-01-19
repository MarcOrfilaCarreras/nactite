from typing import Any
from typing import Dict
from typing import Optional

import requests
from requests import HTTPError
from requests import RequestException
from requests import Timeout

from nactite.common.middleware.cache import cache


class RequestHandler:
    """
    A handler for making HTTP requests with a given session.

    Attributes:
        session (requests.Session): The session to use for making requests.
        headers (dict): A dictionary of headers included in each request by default.
    """

    def __init__(self, *, session: requests.Session, headers: dict = {}) -> 'RequestHandler':
        """
        Initializes the RequestHandler with a session.

        Args:
            session (requests.Session): A session to use for making requests.
            headers (dict): A dictionary of headers to use for making requests.
        """

        self.session = session
        self.headers = headers

    @cache()
    def get(self, *, url: str, params: Optional[Dict[str, Any]] = None, cache: bool = True, cache_table: str = None) -> Optional[requests.Response]:
        """
        Sends a GET request to the specified URL with optional query parameters.

        Args:
            url (str): The URL to send the GET request to.
            params (Optional[Dict[str, Any]]): Optional dictionary of query string parameters.
            cache (bool, optional): Specifies if caching should be used for this request. Defaults to True.
            cache_table (Optional[str], optional): The cache table name to use. Defaults to None.

        Returns:
            Optional[requests.Response]: The response object if the request was successful, None otherwise.

        Raises:
            ValueError: If the URL is invalid.
            requests.HTTPError: If an HTTP error occurred.
            requests.RequestException: If a request exception occurred.
        """

        try:
            if not isinstance(url, str) or not url.strip():
                raise ValueError(
                    'Invalid URL. URL must be a non-empty string.')

            response = self.session.get(
                url, headers=self.headers, params=params)
            response.raise_for_status()
            return response

        except (RequestException, HTTPError, Timeout) as e:
            return None

    def post(self, *, url: str, data: Optional[Dict[str, Any]] = None) -> Optional[requests.Response]:
        """
        Sends a POST request to the specified URL with optional JSON data.

        Args:
            url (str): The URL to send the POST request to.
            data (Optional[Dict[str, Any]]): Optional dictionary to send as JSON data.

        Returns:
            Optional[requests.Response]: The response object if the request was successful, None otherwise.

        Raises:
            ValueError: If the URL is invalid.
            requests.HTTPError: If an HTTP error occurred.
            requests.RequestException: If a request exception occurred.
        """

        try:
            if not isinstance(url, str) or not url.strip():
                raise ValueError(
                    'Invalid URL. URL must be a non-empty string.')

            response = self.session.post(
                url, headers=self.headers, json=data)
            response.raise_for_status()
            return response

        except (RequestException, HTTPError, Timeout) as e:
            return None
