from datetime import datetime
from typing import Dict
from typing import Optional


def is_a_date(*, date_str: str) -> bool:
    """
    Validates if a date string is in the format 'YYYY-MM-DD'.

    Args:
        date_str (str): The date as a string in the format 'YYYY-MM-DD'.

    Returns:
        bool: True if the date is valid, False otherwise.
    """

    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False
