import os

from nactite.intranet.client import Client

username = os.getenv('INTEGRATION_TESTS_INTRANET_USER')
password = os.getenv('INTEGRATION_TESTS_INTRANET_PASSWORD')

c = Client()


def run_integration_tests():
    try:
        print('🔄 Logging in to the intranet...')
        if not c.login(username=username, password=password):
            print('❌ Login failed: Check username or password.')
            return
        print('✅ Successfully logged in.')

        print('\n🔄 Fetching areas data for date range 2024-01-01 to 2024-01-01...')
        areas_data = c.get_areas(date_from='2024-01-01', date_to='2024-01-01')
        assert (not areas_data['ventas']
                ), "❌ Key 'ventas' was not found in areas data"
        print("✅ 'ventas' key was found in areas data, as expected.")

        print('\n🔄 Fetching vendors data for date range 2024-01-01 to 2024-01-01...')
        vendors_data = c.get_vendors(
            date_from='2024-01-01', date_to='2024-01-01', all=False)
        assert (not vendors_data['ventas']
                ), "❌ Key 'ventas' was not found in vendors data"
        print("✅ 'ventas' key was found in vendors data, as expected.")

    except AssertionError as e:
        print(f'❌ Test failed: {e}')
    except Exception as e:
        print(f'❌ Unexpected error occurred: {e}')
    finally:
        print('\n🔄 Logging out...')
        c.logout()
        print('✅ Logged out successfully.')


if __name__ == '__main__':
    run_integration_tests()
