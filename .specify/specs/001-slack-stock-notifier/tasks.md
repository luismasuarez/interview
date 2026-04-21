# Tasks: Slack Stock Notifier

**Input**: `.specify/specs/001-slack-stock-notifier/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup

**Purpose**: Project initialization and structure

- [x] T001 Create project structure: `slack_notifier/`, `tests/unit/`, `tests/integration/`, `pyproject.toml`, `.env.example`
- [x] T002 Configure `pyproject.toml` with dependencies: `apscheduler`, `requests`, `python-dotenv`, `sqlalchemy`, `pytest`, `pytest-mock`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared infrastructure required by all user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Implement `slack_notifier/config.py` — load and validate env vars (`SLACK_WEBHOOK_URL`, `DATABASE_URL`, `DAILY_SUMMARY_HOUR`, `DAILY_SUMMARY_MINUTE`, `STOCK_CHECK_INTERVAL_MINUTES`); raise `ValueError` with clear message on missing/invalid values
- [x] T004 [P] Implement `slack_notifier/db.py` — SQLAlchemy engine setup + `get_daily_summary(date) -> list[dict]` and `get_low_stock_products() -> list[dict]` using queries from data-model.md
- [x] T005 [P] Implement `slack_notifier/slack.py` — `send_message(text: str) -> None` with single retry after 30s on non-200 response; log success and failure
- [x] T006 [P] Write unit tests for config validation in `tests/unit/test_config.py`

**Checkpoint**: Foundation ready — all shared modules tested and working ✅

---

## Phase 3: User Story 1 — Daily Purchase Summary (Priority: P1) 🎯 MVP

**Goal**: Manager receives a correctly formatted daily Slack summary grouped by buyer

**Independent Test**: Run `daily_summary_job()` manually → verify Slack message arrives with correct buyer/product grouping

- [x] T007 [P] [US1] Write unit tests for `daily_summary_job()` in `tests/unit/test_jobs.py`
- [x] T008 [P] [US1] Write unit tests for `slack.send_message` retry logic in `tests/unit/test_slack.py`
- [x] T009 [US1] Implement `daily_summary_job()` in `slack_notifier/jobs.py`
- [x] T010 [US1] Write integration test in `tests/integration/test_jobs_integration.py`

**Checkpoint**: `daily_summary_job()` fully functional and tested independently ✅

---

## Phase 4: User Story 2 — Low Stock Alert (Priority: P2)

**Goal**: Manager receives a Slack alert listing all products below their minimum threshold

**Independent Test**: Insert a product with `stock < min_stock` → run `stock_alert_job()` → verify alert arrives

- [x] T011 [P] [US2] Write unit tests for `stock_alert_job()` in `tests/unit/test_jobs.py`
- [x] T012 [US2] Implement `stock_alert_job()` in `slack_notifier/jobs.py`
- [x] T013 [US2] Write integration test in `tests/integration/test_jobs_integration.py`

**Checkpoint**: Both jobs work independently ✅

---

## Phase 5: User Story 3 — Scheduler Reliability (Priority: P3)

**Goal**: Both jobs run automatically on schedule without manual intervention

**Independent Test**: Start scheduler with short intervals → verify both jobs execute and produce log output

- [x] T014 [US3] Implement `slack_notifier/scheduler.py`
- [x] T015 [US3] Write integration test in `tests/integration/test_scheduler.py`

**Checkpoint**: Full system runs end-to-end automatically ✅

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T016 [P] Populate `.env.example` with all required keys and inline comments
- [ ] T017 [P] Validate `quickstart.md` steps work end-to-end from a clean checkout
- [x] T018 Run full test suite (`pytest`) and confirm all tests pass

---

## Dependencies & Execution Order

- **Phase 1** → no dependencies
- **Phase 2** → depends on Phase 1; BLOCKS Phases 3–5
- **Phase 3 (US1)** → depends on Phase 2; independent of US2/US3
- **Phase 4 (US2)** → depends on Phase 2; independent of US1/US3
- **Phase 5 (US3)** → depends on T009 (US1) + T012 (US2)
- **Phase 6** → depends on all phases complete

### Parallel Opportunities

Within Phase 2: T004, T005, T006 can run in parallel (different files)  
Within Phase 3: T007, T008 can run in parallel before T009  
Within Phase 4: T011 can run in parallel before T012  
US1 and US2 phases can be worked in parallel by different developers after Phase 2

---

## Implementation Strategy

### MVP (User Story 1 only)

1. Phase 1 → Phase 2 → Phase 3 → validate → done
2. Manager gets daily summaries. Ship it.

### Full delivery

Add Phase 4 (stock alerts) → Phase 5 (scheduler) → Phase 6 (polish)

---

## Summary

| Phase | Tasks | Parallelizable |
|-------|-------|---------------|
| Setup | 2 | 0 |
| Foundational | 4 | 3 |
| US1 Daily Summary | 4 | 2 |
| US2 Stock Alert | 3 | 1 |
| US3 Scheduler | 2 | 0 |
| Polish | 3 | 2 |
| **Total** | **18** | **8** |
