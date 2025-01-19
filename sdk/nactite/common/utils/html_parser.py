import re
from typing import Optional

from bs4 import BeautifulSoup


def extract_js_variable(*, html: str, var_name: str, var_type: str) -> Optional[str]:
    """
    Extracts the value of a JavaScript variable from an HTML document.

    Args:
        html (str): The HTML content as a string.
        var_name (str): The name of the JavaScript variable to extract.
        var_type (str): The type of the JavaScript variable (e.g., 'var', 'let', 'const').

    Returns:
        Optional[str]: The value of the JavaScript variable if found, None otherwise.

    Raises:
        ValueError: If html, var_name, or var_type is not a valid non-empty string.
    """

    if not isinstance(html, str) or not html.strip():
        raise ValueError('HTML content must be a non-empty string.')

    if not isinstance(var_name, str) or not var_name.strip():
        raise ValueError('Variable name must be a non-empty string.')

    if not isinstance(var_type, str) or not var_type.strip():
        raise ValueError('Variable type must be a non-empty string.')

    soup = BeautifulSoup(html, 'html.parser')
    script_tags = soup.find_all('script')

    # Compile the regex pattern to match the JavaScript variable declaration
    pattern = re.compile(
        rf'{re.escape(var_type)}\s+{re.escape(var_name)}\s*=\s*"(.*?)";')

    for script in script_tags:
        if script.string:
            match = pattern.search(script.string)
            if match:
                return match.group(1)

    return None
