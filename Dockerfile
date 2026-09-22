FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Dependencies first — this layer stays cached until
# pyproject.toml or uv.lock change.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# README.md is needed because pyproject.toml declares it,
# and uv_build refuses to build without it.
COPY README.md ./
COPY src/ ./src/
RUN uv sync --frozen --no-dev

FROM python:3.12-slim-bookworm
RUN groupadd --system --gid 1001 app && \
    useradd --system --uid 1001 --gid app --no-create-home app

WORKDIR /app
COPY --from=builder --chown=app:app /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

USER app
CMD ["python", "-m", "worker"]