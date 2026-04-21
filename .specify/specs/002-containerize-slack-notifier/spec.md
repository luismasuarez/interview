# Feature Specification: Containerize Slack Stock Notifier

**Feature Branch**: `002-containerize-slack-notifier`  
**Created**: 2026-04-21  
**Status**: Draft  

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Run the service with Docker (Priority: P1)

A developer or operator can build a Docker image and run the Slack Stock Notifier as a container, passing configuration via environment variables. The container starts the scheduler and runs until stopped.

**Why this priority**: This is the core deliverable. Without a working container, nothing else matters.

**Independent Test**: Build the image, run `docker run --env-file .env slack-notifier`, verify the scheduler starts and logs appear on stdout.

**Acceptance Scenarios**:

1. **Given** a valid `.env` file, **When** the container starts, **Then** the scheduler initializes and logs both job registrations within 5 seconds.
2. **Given** a missing required env var (e.g., no `SLACK_WEBHOOK_URL`), **When** the container starts, **Then** it exits immediately with a non-zero code and a human-readable error message.
3. **Given** a running container, **When** `docker stop` is sent, **Then** the container shuts down gracefully within 10 seconds (no forced kill).
4. **Given** the container is running, **When** a job fails (e.g., DB unreachable), **Then** the container does NOT crash — it logs the error and continues running.

---

### User Story 2 — Minimal, secure image (Priority: P2)

The Docker image is small, uses a non-root user, and does not include build tools or unnecessary packages in the final image.

**Why this priority**: Security and image size directly affect deployment safety and pull times. Required by Docker best practices.

**Independent Test**: Run `docker image inspect slack-notifier` and verify image size is under 200MB; run `docker run --rm slack-notifier whoami` and verify output is not `root`.

**Acceptance Scenarios**:

1. **Given** the built image, **When** inspected, **Then** the image size is under 200MB.
2. **Given** the built image, **When** the container runs, **Then** the process runs as a non-root user.
3. **Given** the Dockerfile, **When** reviewed, **Then** it uses a multi-stage build: a build stage installs dependencies, a runtime stage contains only the installed package and its runtime dependencies.
4. **Given** the Dockerfile, **When** reviewed, **Then** the base image version is pinned (tag + digest) per Docker best practices.

---

### User Story 3 — Docker Compose for local development (Priority: P3)

A developer can start the full stack (notifier + SQLite or PostgreSQL) with a single `docker compose up` command for local testing.

**Why this priority**: Simplifies onboarding and local testing without requiring manual env setup.

**Independent Test**: Run `docker compose up` from the project root, verify the notifier container starts and connects to the database service.

**Acceptance Scenarios**:

1. **Given** the `docker-compose.yml`, **When** `docker compose up` is run, **Then** both the notifier and database services start without errors.
2. **Given** the compose file, **When** the notifier starts before the DB is ready, **Then** the notifier retries or waits (health check or `depends_on` with condition).
3. **Given** the compose file, **When** reviewed, **Then** secrets (webhook URL) are passed via environment variables, never hardcoded in the file.

---

### Edge Cases

- What if the `DATABASE_URL` points to a host not reachable from inside the container? → Container starts, job logs a DB error, does not crash.
- What if the image is built on a different architecture (arm64 vs amd64)? → Out of scope for MVP; single-platform build is acceptable.
- What if `.env` file is not provided to `docker run`? → Container exits with a clear config validation error (covered by US1 scenario 2).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project MUST include a `Dockerfile` that builds a runnable image of the Slack Stock Notifier.
- **FR-002**: The `Dockerfile` MUST use a multi-stage build: one stage for installing dependencies, one minimal stage for the runtime image.
- **FR-003**: The runtime image MUST run the process as a non-root user.
- **FR-004**: The base image version MUST be pinned to a specific tag and digest to ensure reproducible builds.
- **FR-005**: All configuration (webhook URL, DB URL, schedule) MUST be injected via environment variables at runtime — no config values baked into the image.
- **FR-006**: The container MUST handle `SIGTERM` gracefully and shut down within 10 seconds.
- **FR-007**: The `Dockerfile` MUST include a `.dockerignore` file that excludes `.env`, `.venv`, `__pycache__`, test files, and other non-runtime artifacts from the build context.
- **FR-008**: The project MUST include a `docker-compose.yml` for local development with the notifier service and a database service.
- **FR-009**: The `docker-compose.yml` MUST use a `healthcheck` or `depends_on` condition to ensure the database is ready before the notifier starts.
- **FR-010**: The image MUST produce structured logs to stdout (not to a file inside the container).

### Key Entities

- **Docker Image**: The built artifact. Has a name, tag, and digest. Built from `Dockerfile`.
- **Container**: A running instance of the image. Configured entirely via environment variables.
- **Compose Stack**: The local development environment defined in `docker-compose.yml`. Includes the notifier container and a database container.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The Docker image builds successfully from a clean checkout with `docker build .` in under 3 minutes.
- **SC-002**: The final image size is under 200MB.
- **SC-003**: The container starts and logs scheduler initialization within 5 seconds of `docker run`.
- **SC-004**: The container exits with code 1 and a readable error message within 3 seconds when required env vars are missing.
- **SC-005**: `docker compose up` brings the full local stack online in under 60 seconds.
- **SC-006**: The running process inside the container is not root (verified via `whoami` or `id`).

## Assumptions

- The existing `slack_notifier/` Python package and `pyproject.toml` are the source of truth; the Dockerfile installs from them.
- SQLite is used in the Compose stack for local dev; the notifier connects to it via `DATABASE_URL`.
- No container registry push is required for MVP — local build and run is sufficient.
- Multi-platform builds (arm64/amd64) are out of scope for this spec.
- The `SLACK_WEBHOOK_URL` is always provided at runtime via env var; it is never stored in the image or the compose file.
