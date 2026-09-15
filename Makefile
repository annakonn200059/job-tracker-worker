-include .env
export

.PHONY: run lint test

run:
	uv run python -m worker

lint:
	uv run ruff check .

test:
	uv run pytest
