from nactite.reviews.client import Client


def run_reviews_test():
    try:
        c = Client()

        print("🔄 Fetching store information for 'Ciutadella'...")
        stores = c.get_store('Ciutadella')
        assert stores, "❌ No store found for 'Ciutadella'"
        print('✅ Store information retrieved successfully.')

        store = stores[0]
        business_id = store.get('business_id')
        assert business_id, "❌ 'business_id' not found in store data"
        print(f'✅ Retrieved business ID: {business_id}')

        print('\n🔄 Fetching reviews for business ID...')
        reviews = c.get_reviews(business_id, limit=5)
        assert len(
            reviews) == 5, f'❌ Expected 5 reviews, but got {len(reviews)}'
        print('✅ Correct number of reviews retrieved (5).')

    except AssertionError as e:
        print(f'❌ Test failed: {e}')
    except Exception as e:
        print(f'❌ Unexpected error occurred: {e}')


if __name__ == '__main__':
    run_reviews_test()
