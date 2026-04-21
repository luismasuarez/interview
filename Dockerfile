# syntax=docker/dockerfile:1

# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /build

# Install uv for fast dependency resolution
RUN pip install --no-cache-dir uv==0.11.7

# Copy only the project metadata first to cache the dep-install layer
COPY pyproject.toml .
COPY slack_notifier/ ./slack_notifier/

# Install the package and its runtime dependencies into the system Python
RUN uv pip install --system --no-cache .

# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.13-slim@sha256:d168b8d9eb761f4d3fe305ebd04aeb7e7f2de0297cec5fb2f8f6403244621664 AS runtime

# Create a non-root user with explicit UID (--no-log-init avoids sparse-file bug)
RUN useradd --no-log-init -r -u 1001 -m appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source
COPY slack_notifier/ ./slack_notifier/

USER appuser

# Logs go to stdout (no -u needed; Python is unbuffered via PYTHONUNBUFFERED)
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "slack_notifier.scheduler"]
