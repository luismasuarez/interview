# Research: Containerize Slack Stock Notifier

## Base Image

**Decision**: `python:3.13-slim@sha256:d168b8d9eb761f4d3fe305ebd04aeb7e7f2de0297cec5fb2f8f6403244621664`  
**Rationale**: Official Python image, slim variant (~50MB) has no unnecessary packages. Pinned by digest for reproducibility per Docker best practices.  
**Alternatives considered**: `python:3.13-alpine` — rejected (musl libc causes issues with some C extensions; SQLAlchemy compiles fine but adds complexity); `python:3.13` (full) — rejected (>900MB, unnecessary).

## Dependency Installation in Build Stage

**Decision**: Use `uv pip install --system .` in the builder stage  
**Rationale**: `uv` is 10-100x faster than pip for dependency resolution. Already available in the project. `--system` installs into the system Python, making it easy to copy to the runtime stage.  
**Alternatives considered**: `pip install` — works but slower; virtualenv in container — adds complexity for no benefit in a single-service image.

## Database in Compose

**Decision**: SQLite via bind-mounted volume (`./data:/app/data`)  
**Rationale**: No separate DB container needed. SQLite is a file. The volume persists data across container restarts. Matches the existing dev setup.  
**Alternatives considered**: PostgreSQL container — rejected (over-engineered for local dev; the spec says SQLite for dev).

## Non-root User

**Decision**: `useradd --no-log-init -r -u 1001 appuser` with explicit UID  
**Rationale**: Docker best practices require non-root. Explicit UID (1001) avoids non-deterministic assignment. `--no-log-init` avoids the sparse file disk exhaustion bug documented in Docker best practices.  
**Alternatives considered**: Using default UID — rejected (non-deterministic, harder to manage file permissions on mounted volumes).

## Layer Cache Optimization

**Decision**: `COPY pyproject.toml .` before `COPY slack_notifier/` in builder stage  
**Rationale**: Dependency installation is the slowest step. Copying only `pyproject.toml` first means the dep install layer is only invalidated when dependencies change, not when source code changes.
