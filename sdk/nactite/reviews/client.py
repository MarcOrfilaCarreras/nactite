import datetime
from typing import Any
from typing import List
from typing import Optional
from unidecode import unidecode

import requests

from nactite.common.api.request_handler import RequestHandler
from nactite.common.db.migrator import DatabaseMigrator
from nactite.common.middleware.rate_limiter import RateLimiter
from nactite.reviews import endpoints


class Client:
    """
    A client for interacting with the MAPS DATA API to retrieve store reviews.

    Attributes:
        session (requests.Session): A session for making HTTP requests.
        request_handler (RequestHandler): Handles HTTP requests with caching and error handling.
        rate_limiter (RateLimiter): Limits the number of requests within a specified time period.
        _migration_done (bool): Tracks whether database migrations have been run (class-level attribute).
    """

    _migration_done: bool = False

    def __init__(self) -> None:
        """
        Initializes a new Client instance.
        """

        self.session: requests.Session = requests.Session()
        self.request_handler: RequestHandler = RequestHandler(
            session=self.session, headers=endpoints.HEADERS)
        self.rate_limiter: RateLimiter = RateLimiter(
            max_requests=30, period=60)

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

    def get_store(self, name: str = None, limit: int = 1) -> Optional[List]:
        """
        Retrieves a list of stores based on a query name, limited by a specified number.

        Args:
            name (str): The name or partial name of the store to search for.
            limit (int): The maximum number of store results to return.

        Returns:
            Optional[List[dict]]: A list of dictionaries, each containing store 'business_id' and 'name'.
            Returns None if the request fails or if the rate limit is exceeded.

        Raises:
            Exception: If the rate limit is exceeded.
            ValueError: If the 'name' is not a valid non-empty string or 'limit' is not a positive integer.
        """

        if not self.rate_limiter.allow_request():
            raise Exception('Rate limit exceeded. Try again later.')

        if (name is None) or (isinstance(name, str) == False):
            raise ValueError(
                'Name content must be a non-empty string.')

        if (limit is None) or (isinstance(limit, int) == False):
            raise ValueError(
                'Limit content must be a non-empty integer.')

        params = {'query': f'Intecat iStore {unidecode(name)}', 'limit': f'{limit}'}

        response = self.request_handler.get(
            url=endpoints.SEARCH_ENDPOINT, params=params, cache=True, cache_table='reviews_request_cache')

        response_data = response.json()

        response_data_filtered = []
        for store in response_data['data']:
            response_data_filtered.append({
                'business_id': store['business_id'],
                'name': store['name']
            })

        return response_data_filtered

    def get_reviews(self, store: str = None, limit: int = 1) -> Optional[List]:
        """
        Retrieves a list of reviews for a specified store, limited by a specified number.

        Args:
            store (str): The unique identifier (business_id) of the store for which to retrieve reviews.
            limit (int): The maximum number of review results to return.

        Returns:
            Optional[List[dict]]: A list of dictionaries, each containing review 'timestamp', 'rating', 'text', and 'user'.
            Returns None if the request fails or if the rate limit is exceeded.

        Raises:
            Exception: If the rate limit is exceeded.
            ValueError: If 'store' is not a valid non-empty string or 'limit' is not a positive integer.
        """

        if not self.rate_limiter.allow_request():
            raise Exception('Rate limit exceeded. Try again later.')

        if (store is None) or (isinstance(store, str) == False):
            raise ValueError(
                'Store content must be a non-empty string.')

        if (limit is None) or (isinstance(limit, int) == False):
            raise ValueError(
                'Limit content must be a non-empty integer.')

        params = {'business_id': store, 'limit': f'{limit}', 'sort': 'Newest'}

        response = self.request_handler.get(
            url=endpoints.REVIEWS_ENDPOINT, params=params, cache=False)

        response_data = response.json()

        response_data_filtered = []
        for review in response_data['data']['reviews']:
            response_data_filtered.append({
                'timestamp': review['review_time'],
                'rating': str(review['review_rate'] or ''),
                'text': str(review['review_text'] or ''),
                'user': review['user_name']
            })

        return response_data_filtered
