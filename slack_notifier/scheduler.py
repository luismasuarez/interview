import logging
import signal
import sys

from apscheduler.schedulers.blocking import BlockingScheduler

from slack_notifier.config import load_config
from slack_notifier.jobs import daily_summary_job, stock_alert_job

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    cfg = load_config()
    scheduler = BlockingScheduler()

    scheduler.add_job(
        daily_summary_job,
        trigger="cron",
        hour=cfg.DAILY_SUMMARY_HOUR,
        minute=cfg.DAILY_SUMMARY_MINUTE,
        kwargs={"database_url": cfg.DATABASE_URL, "webhook_url": cfg.SLACK_WEBHOOK_URL},
        id="daily_summary",
        misfire_grace_time=300,
    )

    scheduler.add_job(
        stock_alert_job,
        trigger="interval",
        minutes=cfg.STOCK_CHECK_INTERVAL_MINUTES,
        kwargs={"database_url": cfg.DATABASE_URL, "webhook_url": cfg.SLACK_WEBHOOK_URL},
        id="stock_alert",
        misfire_grace_time=60,
    )

    logger.info(
        "Scheduler started — daily summary at %02d:%02d, stock check every %d min",
        cfg.DAILY_SUMMARY_HOUR,
        cfg.DAILY_SUMMARY_MINUTE,
        cfg.STOCK_CHECK_INTERVAL_MINUTES,
    )

    def _shutdown(sig, frame):
        logger.info("Shutting down scheduler")
        scheduler.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    scheduler.start()


if __name__ == "__main__":
    main()
