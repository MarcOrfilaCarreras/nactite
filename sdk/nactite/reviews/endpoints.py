import os

BASE_URL = 'https://maps-data.p.rapidapi.com'

SEARCH_ENDPOINT = f'{BASE_URL}/searchmaps.php'
REVIEWS_ENDPOINT = f'{BASE_URL}/reviews.php'

HEADERS = {
    'x-rapidapi-key': os.getenv('RAPIDAPI_REVIEWS_KEY') or '',
    'x-rapidapi-host': 'maps-data.p.rapidapi.com'
}
