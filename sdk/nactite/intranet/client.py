import time
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional

import requests

from nactite.common.api.request_handler import RequestHandler
from nactite.common.db.migrator import DatabaseMigrator
from nactite.common.middleware.rate_limiter import RateLimiter
from nactite.common.utils.html_parser import extract_js_variable
from nactite.common.utils.validation import is_a_date
from nactite.intranet import endpoints


class Client:
    """
    A client for interacting with a web service that requires authentication and rate limiting.

    Attributes:
        id (Optional[str]): The user's ID after login.
        area (Optional[str]): The user's area after login.
        session (requests.Session): The session object used for making HTTP requests.
        request_handler (RequestHandler): The handler for managing requests.
        rate_limiter (RateLimiter): The rate limiter to control the number of requests.
    """

    _migration_done: bool = False

    def __init__(self) -> None:
        """
        Initializes a new Client instance.
        """

        self.id: Optional[str] = None
        self.area: Optional[str] = None
        self._last_check_login = None
        self.session: requests.Session = requests.Session()
        self.request_handler: RequestHandler = RequestHandler(
            session=self.session, headers=endpoints.HEADERS)
        self.rate_limiter: RateLimiter = RateLimiter(
            max_requests=1000, period=3600)

        if not Client._migration_done:
            self._run_migrations()

    def _run_migrations(self):
        """
        Run database migrations to ensure that the database schema is up-to-date.

        This method is called only once to perform necessary migrations.
        """

        migrator = DatabaseMigrator()
        migrator.migrate()

        Client._migration_done = True

    def login(self, *, username: str = None, password: str = None) -> bool:
        """
        Logs in the user with the given username and password.

        Args:
            username (str): The username for login.
            password (str): The password for login.

        Returns:
            bool: True if login is successful, False otherwise.

        Raises:
            Exception: If rate limit is exceeded.
            ValueError: If login fails (session cookie not found).
        """

        if not isinstance(username, str) or not username.strip():
            raise ValueError('Username content must be a non-empty string.')

        if not isinstance(password, str) or not password.strip():
            raise ValueError('Password content must be a non-empty string.')

        if not self.rate_limiter.allow_request():
            raise Exception('Rate limit exceeded. Try again later.')

        data = {'username': username, 'password': password}
        response = self.request_handler.post(
            url=endpoints.LOGIN_AUTH_ENDPOINT, data=data)

        if 'PHPSESSID' not in response.cookies:
            raise Exception('Login failed: session cookie not found')

        return self._is_logged_in()

    def logout(self) -> bool:
        """
        Logs out the user.

        Returns:
            bool: True if logout is successful, False otherwise.

        Raises:
            Exception: If rate limit is exceeded.
        """

        if not self.rate_limiter.allow_request():
            raise Exception('Rate limit exceeded. Try again later.')

        response = self.request_handler.post(
            url=endpoints.LOGOUT_AUTH_ENDPOINT)

        if not self._is_logged_in():
            return False

        self.id = None
        self.area = None
        self.session = requests.Session()

        return True

    def get_areas(self, date_from: str = None, date_to: str = None, all: bool = False, custom_params: dict = {}) -> Optional[Dict[str, Any]]:
        """
        Retrieves areas data within the specified date range.

        Args:
            date_from (Optional[str]): The start date in 'YYYY-MM-DD' format. Defaults to today.
            date_to (Optional[str]): The end date in 'YYYY-MM-DD' format. Defaults to today.
            all (bool): Whether to return all areas or just the current user's area.
            custom_params (dict): Additional url parameters.

        Returns:
            Optional[Dict[str, Any]]: The areas data.

        Raises:
            Exception: If rate limit is exceeded.
            ValueError: If the user is not logged in.
        """

        if not self.rate_limiter.allow_request():
            raise Exception('Rate limit exceeded. Try again later.')

        if not self._is_logged_in():
            return None

        date_from = date_from or datetime.now().strftime('%Y-%m-%d')
        date_to = date_to or datetime.now().strftime('%Y-%m-%d')

        if (is_a_date(date_str=date_from) is False) or (is_a_date(date_str=date_to) is False):
            raise ValueError(
                'Dates content must be a non-empty string following this patter yyyy-mm-dd.')

        params = {'from': date_from, 'to': date_to}

        if len(custom_params.keys()) > 0:
            params.update(custom_params)

        response = self.request_handler.get(
            url=endpoints.AREAS_RANKING_ENDPOINT, params=params, cache_table='intranet_request_cache')

        if hasattr(response, 'headers') and ('X-Nactite-Cache' in response.headers.keys()) and response.headers['X-Nactite-Cache'] == 'HIT':
            self.rate_limiter.drop_request()

        response_data = response.json()

        if not all:
            return response_data['result']['data'][self.area]

        return response_data['result']['data']

    def get_vendors(self, date_from: str = None, date_to: str = None, all: bool = True, custom_params: dict = {}) -> Optional[Dict[str, Any]]:
        """
        Retrieves vendors data within the specified date range.

        Args:
            date_from (Optional[str]): The start date in 'YYYY-MM-DD' format. Defaults to today.
            date_to (Optional[str]): The end date in 'YYYY-MM-DD' format. Defaults to today.
            all (bool): Whether to return all vendors or just the current user's vendors.
            custom_params (dict): Additional url parameters.

        Returns:
            Optional[Dict[str, Any]]: The vendors data.

        Raises:
            Exception: If rate limit is exceeded.
            ValueError: If the user is not logged in.
        """

        if not self.rate_limiter.allow_request():
            raise Exception('Rate limit exceeded. Try again later.')

        if not self._is_logged_in():
            return None

        date_from = date_from or datetime.now().strftime('%Y-%m-%d')
        date_to = date_to or datetime.now().strftime('%Y-%m-%d')

        if (is_a_date(date_str=date_from) is False) or (is_a_date(date_str=date_to) is False):
            raise ValueError(
                'Dates content must be a non-empty string following this patter yyyy-mm-dd.')

        params = {'from': date_from, 'to': date_to}

        if len(custom_params.keys()) > 0:
            params.update(custom_params)

        response = self.request_handler.get(
            url=endpoints.VENDOORS_RANKING_ENDPOINT, params=params, cache_table='intranet_request_cache')

        if hasattr(response, 'headers') and ('X-Nactite-Cache' in response.headers.keys()) and response.headers['X-Nactite-Cache'] == 'HIT':
            self.rate_limiter.drop_request()

        response_data = response.json()

        if not all:
            return response_data['result'][self.id]

        return response_data['result']

    def _is_logged_in(self) -> bool:
        """
        Checks if the user is logged in by verifying the presence of session data.

        Returns:
            bool: True if the user is logged in, False otherwise.

        Raises:
            Exception: If rate limit is exceeded.
        """

        current_time = time.time()

        if (self._last_check_login is not None) and (current_time - self._last_check_login) < 15:
            return True

        response = self.request_handler.get(
            url=endpoints.BASE_URL, cache=False)

        id = extract_js_variable(
            html=response.text, var_name='g_v', var_type='var')
        area = extract_js_variable(
            html=response.text, var_name='g_a', var_type='var')

        if id:
            self.id = id
        if area:
            self.area = area

        is_logged_in = self.id is not None and self.area is not None

        self._last_check_login = current_time

        return is_logged_in
