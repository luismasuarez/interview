# Tasks: Containerize Slack Stock Notifier

**Input**: `.specify/specs/002-containerize-slack-notifier/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅

---

## Phase 1: Setup

- [x] T001 Create `.dockerignore` excluding `.env`, `.venv`, `__pycache__`, `tests/`, `data/`, `.git`, `*.md`, `.specify/`
- [x] T002 Create `data/` directory with `.gitkeep` for SQLite bind-mount

---

## Phase 2: US1 — Dockerfile (Priority: P1) 🎯 MVP

**Goal**: `docker build . && docker run --env-file .env slack-notifier` works

- [x] T003 Write `Dockerfile` — multi-stage: builder stage installs deps with `uv pip install --system .`; runtime stage copies site-packages + source, creates non-root user (UID 1001), sets `CMD ["python", "-m", "slack_notifier.scheduler"]`
- [x] T004 [US1] Verify image builds: `docker build -t slack-notifier .` ✅
- [x] T005 [US1] Verify missing env var exits with code 1 ✅ (ValueError: Missing required config: SLACK_WEBHOOK_URL)

**Checkpoint**: Image builds and runs correctly ✅

---

## Phase 3: US2 — Image quality (Priority: P2)

- [x] T006 [US2] Image size: **72.9 MB** (< 200MB) ✅
- [x] T007 [US2] Non-root: uid=1001(appuser) ✅

**Checkpoint**: Image is minimal and secure ✅

---

## Phase 4: US3 — Docker Compose (Priority: P3)

- [x] T008 [US3] Write `docker-compose.yml`
- [x] T009 [US3] Update `.env.example` with container DATABASE_URL note
- [x] T010 [US3] Verify `docker compose up` starts without errors

**Checkpoint**: Full local stack works ✅

---

## Phase 5: Polish

- [x] T011 Add `data/` to `.gitignore`
- [x] T012 Commit all container files

---

## Summary

| Phase | Tasks | Status |
|-------|-------|--------|
| Setup | 2 | ✅ |
| US1 Dockerfile | 3 | ✅ |
| US2 Image quality | 2 | ✅ |
| US3 Compose | 3 | ✅ |
| Polish | 2 | ✅ |
| **Total** | **12** | **12/12** |
