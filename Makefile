.PHONY: lint check format install run clean test test-smoke test-cov debug

# Run type checking with basedpyright
lint:
	uv run basedpyright bot.py

# Format code with black
format:
	uv run ruff format .

# Check code with ruff
check:
	uv run ruff check . --fix

# Install dependencies
install:
	uv sync

# Run the bot
run:
	uv run python bot.py

# Run debug server for prompt testing
debug:
	uv run python debug_server.py

# Run all tests
test:
	uv run pytest tests/ -v

# Run smoke tests only
test-smoke:
	uv run pytest tests/test_cover_letter/test_basic.py -v

# Run tests with coverage
test-cov:
	uv run pytest tests/ --cov=cover_letter --cov-report=html --cov-report=term

# Clean cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

# Full check: format, lint, and check
full-check: format check lint
	@echo "All checks completed!"

# Install dev dependencies
install-dev:
	uv add --dev basedpyright ruff black

# Help
help:
	@echo "Available targets:"
	@echo "  lint        - Run type checking with basedpyright"
	@echo "  format      - Format code with black"
	@echo "  check       - Check code with ruff"
	@echo "  install     - Install dependencies"
	@echo "  run         - Run the bot"
	@echo "  debug       - Run debug server for prompt testing"
	@echo "  test        - Run all tests"
	@echo "  test-smoke  - Run smoke tests only"
	@echo "  test-cov    - Run tests with coverage"
	@echo "  clean       - Clean cache files"
	@echo "  full-check  - Run format, check, and lint"
	@echo "  install-dev - Install development dependencies"
	@echo "  help        - Show this help" 