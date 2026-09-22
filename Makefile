-include .env
export

SHA   := $(shell git rev-parse --short HEAD)
DIRTY := $(shell git diff --quiet && git diff --cached --quiet || echo "-dirty")
TAG   := $(SHA)$(DIRTY)

# Inside a container, localhost is the container itself.
DOCKER_DATABASE_URL := $(subst localhost,host.docker.internal,$(DATABASE_URL))

.PHONY: run lint test tag image run-image sizes

run:
	uv run python -m worker

lint:
	uv run ruff check .

test:
	uv run pytest

tag:
	@echo $(TAG)

image:
	docker build -t job-tracker-worker:$(TAG) .

run-image:
	docker run --rm --name worker \
	  --env-file .env \
	  -e DATABASE_URL="$(DOCKER_DATABASE_URL)" \
	  job-tracker-worker:$(TAG)

sizes:
	@docker images --filter=reference='job-tracker-*'