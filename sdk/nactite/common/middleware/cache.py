import hashlib
import pickle
import sqlite3
from datetime import datetime
from datetime import timedelta
from functools import wraps
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Union

import requests


class CacheController:
    """
    A class to manage caching of HTTP responses using SQLite and Pickle.

    Attributes:
        db_path (str): Path to the SQLite database file.
    """

    def __init__(self, db_path: str = 'cache.db') -> None:
        """
        Initializes the CacheController with the path to the database file.

        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        """
        Establishes and returns a connection to the SQLite database.

        Returns:
            sqlite3.Connection: The SQLite connection object.
        """
        return sqlite3.connect(self.db_path)

    def save_to_cache(self, id: str, response: Any, cache_table: str) -> None:
        """
        Saves a response to the cache.

        Args:
            id (str): Unique identifier for the cached response.
            response (Any): The response object to cache.
            cache_table (str): The name of the table where the response is cached.
        """
        conn = self._connect()
        cursor = conn.cursor()
        response_pickle = pickle.dumps(response)
        cursor.execute(f'''
        INSERT OR REPLACE INTO {cache_table} (id, response, timestamp)
        VALUES (?, ?, ?)
        ''', (id, response_pickle, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def get_from_cache(self, id: str, cache_table: str) -> Optional[Any]:
        """
        Retrieves a response from the cache.

        Args:
            id (str): Unique identifier for the cached response.
            cache_table (str): The name of the table to retrieve the cached response from.

        Returns:
            Optional[Any]: The cached response, or None if not found.
        """
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(f'''
        SELECT response, timestamp FROM {cache_table} WHERE id = ?
        ''', (id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            response_data, _ = row
            return pickle.loads(response_data)

        return None


cache_controller = CacheController()


def cache() -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to cache the result of an HTTP request function.

    Returns:
        Callable[[Callable[..., Any]], Callable[..., Any]]: The decorator function.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Dict[str, Any]) -> Any:
            cache_flag: Optional[bool] = kwargs.get('cache')
            cache_table: Optional[str] = kwargs.get('cache_table')

            if cache_flag is False or cache_table is None:
                return func(*args, **kwargs)

            url: Optional[str] = kwargs.get('url')
            params: Optional[Dict[str, Any]] = kwargs.get('params')

            if url is None:
                raise ValueError("The 'url' keyword argument is required.")

            if (params) and (('from' in params.keys()) or ('to' in params.keys())):
                current_date = datetime.now().date()
                target_date = current_date - timedelta(days=2)

                date_from_str = params.get('from')
                date_to_str = params.get('to')

                date_from = datetime.strptime(
                    date_from_str, '%Y-%m-%d').date() if date_from_str else None
                date_to = datetime.strptime(
                    date_to_str, '%Y-%m-%d').date() if date_to_str else None

                if (date_from and date_from >= target_date) or (date_to and date_to >= target_date):
                    return func(*args, **kwargs)

            if params:
                url += '&' + \
                    '&'.join(f'{key}={value}' for key, value in params.items())

            id = hashlib.md5(url.encode()).hexdigest()
            cached_response = cache_controller.get_from_cache(
                id, cache_table=cache_table)
            if cached_response is not None:
                if hasattr(cached_response, 'headers'):
                    cached_response.headers['X-Nactite-Cache'] = 'HIT'
                return cached_response

            response = func(*args, **kwargs)

            if hasattr(response, 'headers'):
                response.headers['X-Nactite-Cache'] = 'MISS'

            cache_controller.save_to_cache(
                id, response, cache_table=cache_table)
            return response

        return wrapper

    return decorator
