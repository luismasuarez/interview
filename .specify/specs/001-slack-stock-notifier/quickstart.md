# Quickstart: Slack Stock Notifier

## Prerequisites

- Python 3.11+
- `uv` or `pip`
- A Slack Incoming Webhook URL ([create one here](https://api.slack.com/messaging/webhooks))
- A database with `orders` and `products` tables (see [data-model.md](data-model.md))

## Setup

```bash
# 1. Install dependencies
pip install -e ".[dev]"

# 2. Configure
cp .env.example .env
# Edit .env with your values

# 3. Run tests
pytest

# 4. Start the service
python -m slack_notifier.scheduler
```

## Configuration (.env)

```env
# Required
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
DATABASE_URL=sqlite:///./data.db   # or postgresql://user:pass@host/db

# Schedule (cron format)
DAILY_SUMMARY_HOUR=8
DAILY_SUMMARY_MINUTE=0

# Stock check interval (minutes)
STOCK_CHECK_INTERVAL_MINUTES=30
```

## Verify it works

Trigger jobs manually:

```python
from slack_notifier.jobs import daily_summary_job, stock_alert_job
daily_summary_job()   # Should post to Slack
stock_alert_job()     # Posts only if products are below threshold
```
