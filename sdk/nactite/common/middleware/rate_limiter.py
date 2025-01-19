import time
from typing import List


class RateLimiter:
    """
    A class to implement rate limiting functionality.

    Attributes:
        max_requests (int): Maximum number of requests allowed within the period.
        period (int): Time period in seconds during which the max_requests are allowed.
        requests (List[float]): List to store timestamps of requests.
    """

    def __init__(self, *, max_requests: int = 50, period: int = 60) -> None:
        """
        Initializes a RateLimiter instance.

        Args:
            max_requests (int): Maximum number of requests allowed. Must be a positive integer.
            period (int): Time period in seconds during which max_requests are allowed. Must be a positive integer.

        Raises:
            ValueError: If max_requests or period is not a positive integer.
        """

        if not isinstance(max_requests, int) or max_requests <= 0:
            raise ValueError('max_requests must be a positive integer.')
        if not isinstance(period, int) or period <= 0:
            raise ValueError('period must be a positive integer.')

        self.max_requests = max_requests
        self.period = period
        self.requests: List[float] = []

    def allow_request(self) -> bool:
        """
        Determines if a request can be made based on the rate limit.

        Returns:
            bool: True if the request can be allowed, False otherwise.
        """

        current_time = time.time()

        # Remove timestamps that are older than the allowed period
        self.requests = [r for r in self.requests if r >
                         current_time - self.period]

        if len(self.requests) < self.max_requests:
            self.requests.append(current_time)
            return True

        return False

    def drop_request(self) -> None:
        """
        Removes the last request from the record, if any.
        """
        if self.requests:
            self.requests.pop()
