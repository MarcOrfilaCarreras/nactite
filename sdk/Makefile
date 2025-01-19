ifeq (,$(wildcard .env))
    $(error .env file not found)
else
    include .env
    export $(shell sed 's/=.*//' .env)
endif

test:
	@echo "Starting test task..."

	@echo ""
	@echo "Step 1: Installing dependencies..."
	@echo "----------------------------------------------------"
	@pip install . > /dev/null || { echo "❌ pip install failed"; exit 1; }
	@echo "✅ Dependencies installed successfully."

	@echo ""
	@echo "Step 2: Cleaning up old cache files..."
	@echo "----------------------------------------------------"
	@rm -f cache.db
	@echo "✅ Cache cleared."

	@echo ""
	@echo "Step 3: Running integration tests..."
	@echo "----------------------------------------------------"
	@make run-integration-tests || { echo "❌ Unit tests failed"; exit 1; }

	@echo ""
	@echo "🎉 All steps completed successfully!"

run-integration-tests:
	@echo "🚀 Running reviews integration tests..."
	@python3 tests/integration/reviews.py || { echo "❌ Tests failed"; exit 1; }
	@echo "✅ Reviews tests completed successfully."
	@echo ""
	@echo "🚀 Running intranet integration tests..."
	@python3 tests/integration/intranet.py || { echo "❌ Tests failed"; exit 1; }
	@echo "✅ Intranet tests completed successfully."
	@echo ""
	@echo "🚀 Running sat integration tests..."
	@python3 tests/integration/sat.py || { echo "❌ Tests failed"; exit 1; }
	@echo "✅ SAT tests completed successfully."
