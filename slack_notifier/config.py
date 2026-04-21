import os
from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Missing required config: {key}")
    return value


def _require_int(key: str) -> int:
    value = _require(key)
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Config {key} must be an integer, got: {value!r}")


class Config:
    SLACK_WEBHOOK_URL: str = ""
    DATABASE_URL: str = ""
    DAILY_SUMMARY_HOUR: int = 8
    DAILY_SUMMARY_MINUTE: int = 0
    STOCK_CHECK_INTERVAL_MINUTES: int = 30


def load_config() -> Config:
    cfg = Config()
    cfg.SLACK_WEBHOOK_URL = _require("SLACK_WEBHOOK_URL")
    cfg.DATABASE_URL = _require("DATABASE_URL")
    cfg.DAILY_SUMMARY_HOUR = _require_int("DAILY_SUMMARY_HOUR")
    cfg.DAILY_SUMMARY_MINUTE = _require_int("DAILY_SUMMARY_MINUTE")
    cfg.STOCK_CHECK_INTERVAL_MINUTES = _require_int("STOCK_CHECK_INTERVAL_MINUTES")
    return cfg
