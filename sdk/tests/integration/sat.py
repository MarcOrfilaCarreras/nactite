import os

from nactite.sat.client import Client

username = os.getenv('INTEGRATION_TESTS_SAT_USER')
password = os.getenv('INTEGRATION_TESTS_SAT_PASSWORD')

c = Client()


def run_integration_tests():
    try:
        print('🔄 Logging in to the SAT...')
        if not c.login(username=username, password=password):
            print('❌ Login failed: Check username or password.')
            return
        print('✅ Successfully logged in.')

        service_locations = c.get_service_locations()
        assert len(
            service_locations) >= 1, f'❌ Expected 1 or more locations for services, but got {len(service_locations)}'
        print(
            f'✅ Correct number of service locations retrieved ({len(service_locations)}).')

        origin_locations = c.get_origin_locations()
        assert len(
            origin_locations) >= 1, f'❌ Expected 1 or more locations for origin, but got {len(origin_locations)}'
        print(
            f'✅ Correct number of origin locations retrieved ({len(origin_locations)}).')

        repairs = c.get_repairs(
            service_location='SAT-IBZ', date_from='2024-01-01', date_to='2024-12-31')
        assert len(
            repairs) >= 1, f'❌ Expected 1 or more repairs, but got {len(repairs)}'
        print(f'✅ Correct number of repairs retrieved ({len(repairs)}).')

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
