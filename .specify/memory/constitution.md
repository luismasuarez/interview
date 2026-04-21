<!-- Sync Impact Report
Version change: 0.0.0 → 1.0.0
Added sections: All (initial ratification)
Modified principles: N/A (initial)
Templates requiring updates: ✅ No changes required (greenfield project)
Follow-up TODOs: None
-->

# Slack Stock Notifier Constitution

## Core Principles

### I. Reliability First (NON-NEGOTIABLE)
Notifications MUST be delivered. Any failure to send a scheduled message or stock alert MUST be logged and retried. Silent failures are unacceptable. The system MUST surface errors visibly.

### II. Simplicity Over Abstraction
The MVP MUST use the minimum number of components necessary. No over-engineering. Each module has a single responsibility. Complexity MUST be justified by a concrete requirement.

### III. Configuration-Driven Behavior
All thresholds, schedules, Slack webhook URLs, and data source connections MUST be externalized to configuration. No hardcoded values in business logic.

### IV. Observability
Every scheduled job execution MUST produce a log entry (success or failure). Alerts MUST include enough context (product name, current stock, threshold) for the recipient to act without additional lookups.

### V. Test-First (NON-NEGOTIABLE)
Unit tests MUST be written before implementation for all business logic (stock threshold evaluation, message formatting, summary aggregation). Integration tests MUST cover the Slack delivery path.

## Development Constraints

- Language: Python 3.11+
- Slack integration: Incoming Webhooks only (no OAuth/Bot Token for MVP)
- Scheduler: APScheduler (no OS-level cron dependency)
- Data source: SQLite for development, PostgreSQL-compatible queries for production
- No UI for MVP

## Quality Gates

- All business logic functions MUST have unit test coverage before merging
- No PR merges with failing tests
- Configuration schema MUST be validated at startup; invalid config MUST prevent startup with a clear error message

## Governance

This constitution supersedes all other practices. Amendments require: (1) documented rationale, (2) version bump per semantic versioning, (3) update to this file. All implementation decisions MUST be traceable to a principle above.

**Version**: 1.0.0 | **Ratified**: 2026-04-21 | **Last Amended**: 2026-04-21
