

Worker readme · MD
# Job Tracker Worker
 
Background worker for the job search tracker: parses job postings, extracts
requirements via an LLM, and generates embeddings for CV matching.
 
Part of four repositories — `job-tracker-web`, `job-tracker-api`,
**`job-tracker-worker`**, `job-tracker-infra`.
 
> **Current state:** skeleton. The loop, config, logging and graceful shutdown
> work; `process_one` is a placeholder. Queue, LLM client and embeddings come later.
 
## Stack
 
Python 3.12 · asyncio · uv · structlog · asyncpg
 
## Quick start
 
```bash
cd ../job-tracker-infra && make up && cd -   # PostgreSQL
cp .env.example .env
uv sync
make run
```
 
## Configuration
 
| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | — | **required** |
| `LOG_LEVEL` | `info` | log level |
| `SHUTDOWN_WAIT` | `15` | seconds to finish an in-flight item after SIGTERM |
| `POLL_INTERVAL` | `5` | seconds between polls |
 
## Graceful shutdown
 
On SIGTERM the current item finishes, no new one starts, and the process exits.
If the item outlives `SHUTDOWN_WAIT`, it's cancelled and the exit code is 1.
 
The stop check sits **between** items, never inside one — once there's a real
queue, exiting mid-item means duplicate processing. The idle wait uses
`asyncio.wait_for(stop.wait(), ...)` instead of `sleep()`, so a signal is noticed
immediately rather than after the poll interval.
 
## Container
 
```bash
make image       # job-tracker-worker:<git-sha>, "-dirty" if uncommitted
make run-image   # runs against the local database
make sizes
```
 
Multi-stage: dependencies installed with uv, then only the virtualenv is copied
into `python:3.12-slim`. Runs as non-root (UID 1001).
 
Both stages must use the **same Python version** — the venv references its
interpreter by path.
 
## Development
 
```bash
make lint
make test
```
 






