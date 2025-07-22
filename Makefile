.PHONY: lint check format install run clean

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
	@echo "  clean       - Clean cache files"
	@echo "  full-check  - Run format, check, and lint"
	@echo "  install-dev - Install development dependencies"
	@echo "  help        - Show this help" 