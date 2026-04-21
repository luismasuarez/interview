# Changelog

All notable changes to this project will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2026-04-21

### Added
- Daily purchase summary job — sends a Slack message each morning grouped by buyer
- Low stock alert job — notifies when any product falls below its minimum threshold
- APScheduler-based scheduler with configurable cron and interval triggers
- SQLAlchemy-based DB queries compatible with SQLite and PostgreSQL
- Slack Incoming Webhook delivery with automatic single retry on failure
- Configuration validation at startup with clear error messages
- Multi-stage Docker image (72.9 MB, non-root user, pinned base image digest)
- `docker-compose.yml` for local development with SQLite volume
- 17 unit and integration tests (pytest)
- Smoke test — end-to-end verification with no external dependencies
