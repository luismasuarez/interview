import logging
from collections import defaultdict
from datetime import date, timedelta

from slack_notifier import db, slack

logger = logging.getLogger(__name__)


def daily_summary_job(database_url: str, webhook_url: str) -> None:
    """Send yesterday's purchase summary grouped by buyer."""
    logger.info("daily_summary_job: starting")
    target_date = date.today() - timedelta(days=1)
    try:
        rows = db.get_daily_summary(database_url, target_date)
    except Exception as exc:
        logger.error("daily_summary_job: DB error — %s", exc)
        return

    date_str = target_date.strftime("%d/%m/%Y")
    if not rows:
        text = f"📊 *Resumen de compras del día - {date_str}*\n\nSin compras registradas para este día."
    else:
        by_buyer: dict[str, list[str]] = defaultdict(list)
        for row in rows:
            by_buyer[row["buyer_name"]].append(
                f"{row['product_name']} x{row['total_qty']}"
            )
        lines = "\n".join(
            f"• {buyer}: {', '.join(products)}"
            for buyer, products in sorted(by_buyer.items())
        )
        total = sum(r["total_qty"] for r in rows)
        text = f"📊 *Resumen de compras del día - {date_str}*\n\n{lines}\n\nTotal: {total} unidades"

    slack.send_message(webhook_url, text)
    logger.info("daily_summary_job: done")


def stock_alert_job(database_url: str, webhook_url: str) -> None:
    """Send alert for products below minimum stock threshold."""
    logger.info("stock_alert_job: starting")
    try:
        products = db.get_low_stock_products(database_url)
    except Exception as exc:
        logger.error("stock_alert_job: DB error — %s", exc)
        return

    if not products:
        logger.info("stock_alert_job: all products above threshold, no alert sent")
        return

    lines = "\n".join(
        f"• {p['name']}: {p['stock']} unidades (mínimo: {p['min_stock']})"
        for p in products
    )
    text = f"⚠️ *Alerta de bajo stock*\n\n{lines}"
    slack.send_message(webhook_url, text)
    logger.info("stock_alert_job: done, %d products alerted", len(products))
