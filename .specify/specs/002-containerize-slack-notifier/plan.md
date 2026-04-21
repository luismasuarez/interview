# Implementation Plan: Containerize Slack Stock Notifier

**Branch**: `002-containerize-slack-notifier` | **Date**: 2026-04-21 | **Spec**: [spec.md](spec.md)

## Summary

Add a `Dockerfile` (multi-stage, non-root, pinned base image) and a `docker-compose.yml` (notifier + SQLite via volume) to the existing `slack_notifier` Python package. All configuration is injected at runtime via environment variables. Logs go to stdout.

## Technical Context

**Language/Version**: Python 3.13-slim (runtime stage)  
**Build tool**: `uv` for fast dependency installation in build stage  
**Base image**: `python:3.13-slim@sha256:d168b8d9eb761f4d3fe305ebd04aeb7e7f2de0297cec5fb2f8f6403244621664`  
**Compose DB**: SQLite via bind-mounted volume (no separate DB container needed — SQLite is a file)  
**Target Platform**: linux/amd64  
**Project Type**: Background service / daemon  
**Constraints**: Image < 200MB, non-root user, no secrets in image

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Reliability First | ✅ | Graceful SIGTERM handling already in scheduler.py |
| II. Simplicity | ✅ | Single Dockerfile, single compose file, no orchestration overhead |
| III. Configuration-Driven | ✅ | All config via env vars, no values baked into image |
| IV. Observability | ✅ | Logs to stdout, visible via `docker logs` |
| V. Test-First | ✅ | Build verification (`docker build`) is the test |

No violations.

## Docker Best Practices Applied

From [docs.docker.com/build/building/best-practices](https://docs.docker.com/build/building/best-practices/):

| Practice | Implementation |
|----------|---------------|
| Multi-stage builds | Stage 1 (`builder`): install deps with uv; Stage 2 (`runtime`): copy only site-packages + source |
| Pin base image versions | `python:3.13-slim@sha256:d168b8d9...` |
| Non-root user | `RUN useradd --no-log-init -r -u 1001 appuser` + `USER appuser` |
| `.dockerignore` | Excludes `.env`, `.venv`, `__pycache__`, `tests/`, `*.md`, `.git` |
| No unnecessary packages | Runtime stage has zero apt installs |
| Ephemeral containers | No state in container; DB file mounted as volume |
| COPY over ADD | Use `COPY` for local files (no remote URLs needed) |
| CMD as exec form | `CMD ["python", "-m", "slack_notifier.scheduler"]` |
| Sort multi-line args | Applied to any future `RUN` with multiple packages |
| Leverage build cache | `COPY pyproject.toml` before `COPY slack_notifier/` to cache dep install layer |

## Project Structure

### Documentation (this feature)

```text
.specify/specs/002-containerize-slack-notifier/
├── plan.md
├── research.md
└── tasks.md
```

### Source Code (repository root)

```text
Dockerfile              # Multi-stage build
.dockerignore           # Excludes dev/test artifacts
docker-compose.yml      # Local dev stack (notifier + SQLite volume)
data/                   # SQLite DB directory (bind-mounted, gitignored)
```

## Phase 0: Research

See [research.md](research.md).

## Phase 1: Design

### Dockerfile (multi-stage)

```
Stage 1 — builder (python:3.13-slim):
  WORKDIR /build
  COPY pyproject.toml .
  RUN pip install uv && uv pip install --system .

Stage 2 — runtime (python:3.13-slim@digest):
  RUN useradd --no-log-init -r -u 1001 appuser
  WORKDIR /app
  COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
  COPY --from=builder /usr/local/bin /usr/local/bin
  COPY slack_notifier/ ./slack_notifier/
  USER appuser
  CMD ["python", "-m", "slack_notifier.scheduler"]
```

### docker-compose.yml

```yaml
services:
  notifier:
    build: .
    env_file: .env
    volumes:
      - ./data:/app/data   # SQLite DB file
    restart: unless-stopped
```

SQLite `DATABASE_URL` in `.env`: `sqlite:////app/data/data.db`  
No separate DB service needed — SQLite is a file, mounted as a volume.
