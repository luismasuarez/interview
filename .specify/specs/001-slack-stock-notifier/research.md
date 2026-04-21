# Research: Slack Stock Notifier

## Slack Incoming Webhooks

**Decision**: Use Slack Incoming Webhooks (not Bot Token API)  
**Rationale**: Zero OAuth setup, single URL, sufficient for one-way notifications to one channel  
**Alternatives considered**: Slack Bot Token API — rejected (requires OAuth app, more setup, unnecessary for MVP)

## Scheduler

**Decision**: APScheduler 3.x with `BackgroundScheduler`  
**Rationale**: Pure Python, no OS cron dependency, supports cron-style and interval triggers, runs in-process  
**Alternatives considered**: OS crontab — rejected (requires OS access, harder to configure programmatically); Celery — rejected (requires broker, over-engineered for MVP)

## Database Abstraction

**Decision**: SQLAlchemy Core (not ORM) with SQLite for dev  
**Rationale**: Raw SQL-like queries without ORM overhead; easy to swap to PostgreSQL by changing the connection string  
**Alternatives considered**: Raw sqlite3 module — rejected (not portable to PostgreSQL); Full ORM — rejected (unnecessary complexity for read-only queries)

## Retry Strategy

**Decision**: Single retry after 30-second delay using a simple try/except + sleep  
**Rationale**: Slack webhooks are reliable; one retry covers transient network issues without complexity  
**Alternatives considered**: Exponential backoff library — rejected (over-engineered for MVP with one recipient)

## Configuration

**Decision**: `python-dotenv` loading from `.env` file, validated at startup with explicit error messages  
**Rationale**: Standard Python practice, works in both dev and production (env vars override .env)  
**Alternatives considered**: YAML config file — rejected (extra dependency, .env is simpler for secrets)

## Message Formatting

**Decision**: Plain Slack markdown (mrkdwn) with emoji prefixes, no Block Kit  
**Rationale**: Sufficient readability, no JSON complexity, works in all Slack clients  
**Alternatives considered**: Block Kit — rejected (more complex, not needed for text-only summaries)
