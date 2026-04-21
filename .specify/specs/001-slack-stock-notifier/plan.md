# Implementation Plan: Slack Stock Notifier

**Branch**: `001-slack-stock-notifier` | **Date**: 2026-04-21 | **Spec**: [spec.md](spec.md)

## Summary

Build a Python service that queries a SQLite/PostgreSQL database for daily purchase data and product stock levels, then sends formatted Slack messages via Incoming Webhook: a daily summary grouped by buyer (scheduled at a configurable time) and periodic stock alerts when products fall below configured thresholds. APScheduler handles scheduling; all configuration is externalized to a `.env` / config file.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: `apscheduler`, `requests`, `python-dotenv`, `sqlalchemy` (query abstraction), `pytest`  
**Storage**: SQLite (dev) — SQLAlchemy queries are PostgreSQL-compatible for production  
**Testing**: pytest + pytest-mock  
**Target Platform**: Linux server (runs as a long-lived process or via systemd)  
**Project Type**: CLI service / background daemon  
**Performance Goals**: Each job completes in under 10 seconds; Slack delivery under 5 seconds  
**Constraints**: No UI, no OAuth, single Slack channel, read-only DB access  
**Scale/Scope**: Single manager recipient, tens of products, hundreds of orders per day

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Reliability First | ✅ | Retry logic on Slack delivery; all failures logged |
| II. Simplicity | ✅ | 5 modules, no unnecessary abstractions |
| III. Configuration-Driven | ✅ | All thresholds, schedule, webhook URL in config |
| IV. Observability | ✅ | Structured logging on every job execution |
| V. Test-First | ✅ | Unit tests for business logic before implementation |

No violations.

## Project Structure

### Documentation (this feature)

```text
.specify/specs/001-slack-stock-notifier/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── slack-messages.md
└── tasks.md
```

### Source Code (repository root)

```text
slack_notifier/
├── config.py          # Load & validate config from env/file
├── db.py              # SQLAlchemy queries (daily summary, stock levels)
├── slack.py           # send_message(text) with retry
├── jobs.py            # daily_summary_job(), stock_alert_job()
└── scheduler.py       # APScheduler setup & entry point

tests/
├── unit/
│   ├── test_db.py
│   ├── test_slack.py
│   └── test_jobs.py
└── integration/
    └── test_scheduler.py

.env.example           # Template with all required config keys
pyproject.toml         # Dependencies & project metadata
```

**Structure Decision**: Single flat package. No sub-packages needed at MVP scale.

## Phase 0: Research

See [research.md](research.md).

## Phase 1: Design Artifacts

See [data-model.md](data-model.md), [contracts/slack-messages.md](contracts/slack-messages.md), [quickstart.md](quickstart.md).
