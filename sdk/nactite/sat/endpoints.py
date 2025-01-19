BASE_URL = 'https://sat.intecat.com'

LOGIN_AUTH_ENDPOINT = f'{BASE_URL}/api/auth/login'
LOGOUT_AUTH_ENDPOINT = f'{BASE_URL}/api/auth/logout'

SERVICE_LOCATIONS_ENDPOINT = f'{BASE_URL}/reparaciones'
REPAIRS_ENDPOINT = f'{BASE_URL}/api/reparaciones/'

HEADERS = {
    'authority': 'sat.intecat.com',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'origin': 'https://sat.intecat.com',
    'referer': 'https://sat.intecat.com/',
    'sec-ch-ua': '"Brave";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}
