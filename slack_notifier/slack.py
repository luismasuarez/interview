import logging
import time
import requests

logger = logging.getLogger(__name__)


def send_message(webhook_url: str, text: str) -> None:
    """POST a message to Slack. Retries once on failure."""
    payload = {"text": text}
    for attempt in range(2):
        try:
            resp = requests.post(webhook_url, json=payload, timeout=10)
            if resp.status_code == 200:
                logger.info("Slack message delivered (attempt %d)", attempt + 1)
                return
            logger.warning(
                "Slack delivery failed (attempt %d): HTTP %d — %s",
                attempt + 1, resp.status_code, resp.text,
            )
        except requests.RequestException as exc:
            logger.warning("Slack delivery error (attempt %d): %s", attempt + 1, exc)
        if attempt == 0:
            time.sleep(30)
    logger.error("Slack message could not be delivered after 2 attempts")
