import time
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional

import requests
from bs4 import BeautifulSoup

from nactite.common.api.request_handler import RequestHandler
from nactite.common.db.migrator import DatabaseMigrator
from nactite.common.middleware.rate_limiter import RateLimiter
from nactite.common.utils.html_parser import extract_js_variable
from nactite.common.utils.validation import is_a_date
from nactite.sat import endpoints


class Client:
    """
    A client for interacting with a web service that requires authentication and rate limiting.

    Attributes:
        session (requests.Session): The session object used for making HTTP requests.
        request_handler (RequestHandler): The handler for managing requests.
        rate_limiter (RateLimiter): The rate limiter to control the number of requests.
    """

    _migration_done: bool = False

    def __init__(self) -> None:
        """
        Initializes a new Client instance.
        """

        self._last_check_login = None
        self.session: requests.Session = requests.Session()
        self.request_handler: RequestHandler = RequestHandler(
            session=self.session, headers=endpoints.HEADERS)
        self.rate_limiter: RateLimiter = RateLimiter(
            max_requests=50, period=3600)

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

        self.session = requests.Session()

        return True

    def get_service_locations(self) -> Optional[Dict[str, Any]]:
        if not self.rate_limiter.allow_request():
            raise Exception('Rate limit exceeded. Try again later.')

        if not self._is_logged_in():
            return None

        response = self.request_handler.get(
            url=endpoints.SERVICE_LOCATIONS_ENDPOINT, cache=True, cache_table='sat_request_cache')
        response_data = response.text

        soup = BeautifulSoup(response_data, 'html.parser')
        script_tags = soup.find_all('script')

        data = []

        for _ in soup.find_all('ul', id='filtro-area-reparacion'):
            for location in _.find_all('li'):
                data.append(
                    {
                        'key': location.get('data-code'),
                        'name': location.get_text()
                    }
                )

        return data

    def get_origin_locations(self) -> Optional[Dict[str, Any]]:
        if not self.rate_limiter.allow_request():
            raise Exception('Rate limit exceeded. Try again later.')

        if not self._is_logged_in():
            return None

        response = self.request_handler.get(
            url=endpoints.SERVICE_LOCATIONS_ENDPOINT, cache=True, cache_table='sat_request_cache')
        response_data = response.text

        soup = BeautifulSoup(response_data, 'html.parser')
        script_tags = soup.find_all('script')

        data = []

        for _ in soup.find_all('ul', id='filtro-area-origen'):
            for location in _.find_all('li'):
                data.append(
                    {
                        'key': location.get('data-code'),
                        'name': location.get_text()
                    }
                )

        return data

    def get_repairs(self, origin_location: str = '', service_location: str = '', date_from: str = None, date_to: str = None) -> Optional[Dict[str, Any]]:
        if not self.rate_limiter.allow_request():
            raise Exception('Rate limit exceeded. Try again later.')

        if not self._is_logged_in():
            return None

        date_from = date_from or datetime.now().strftime('%Y-%m-%d')
        date_to = date_to or datetime.now().strftime('%Y-%m-%d')

        if (is_a_date(date_str=date_from) is False) or (is_a_date(date_str=date_to) is False):
            raise ValueError(
                'Dates content must be a non-empty string following this patter yyyy-mm-dd.')

        params = {'desde': date_from, 'hasta': date_to,
                  'areaorigen': origin_location, 'areareparacion': service_location}

        response = self.request_handler.get(
            url=endpoints.REPAIRS_ENDPOINT, params=params, cache=True, cache_table='sat_request_cache')

        if response.status_code != 200:
            return []

        response_data = response.json()

        data = []

        for repair in response_data['result']:
            data.append(
                {
                    'id': repair['idreparacion'],
                    'code': repair['codreparacion'],
                    'device': repair['equipo'],
                    'status': repair['estado'],
                    'cost': repair['total'] or 0
                }
            )

        return data

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

        check = extract_js_variable(
            html=response.text, var_name='g_tipo', var_type='var')

        self._last_check_login = current_time

        return check is not None
