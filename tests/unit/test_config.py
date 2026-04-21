import pytest
from unittest.mock import patch
from slack_notifier.config import load_config


def test_load_config_success(monkeypatch):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/test")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
    monkeypatch.setenv("DAILY_SUMMARY_HOUR", "8")
    monkeypatch.setenv("DAILY_SUMMARY_MINUTE", "0")
    monkeypatch.setenv("STOCK_CHECK_INTERVAL_MINUTES", "30")
    cfg = load_config()
    assert cfg.SLACK_WEBHOOK_URL == "https://hooks.slack.com/test"
    assert cfg.DAILY_SUMMARY_HOUR == 8
    assert cfg.STOCK_CHECK_INTERVAL_MINUTES == 30


def test_missing_webhook_raises(monkeypatch):
    monkeypatch.delenv("SLACK_WEBHOOK_URL", raising=False)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
    monkeypatch.setenv("DAILY_SUMMARY_HOUR", "8")
    monkeypatch.setenv("DAILY_SUMMARY_MINUTE", "0")
    monkeypatch.setenv("STOCK_CHECK_INTERVAL_MINUTES", "30")
    with pytest.raises(ValueError, match="SLACK_WEBHOOK_URL"):
        load_config()


def test_invalid_int_raises(monkeypatch):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/test")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
    monkeypatch.setenv("DAILY_SUMMARY_HOUR", "not-a-number")
    monkeypatch.setenv("DAILY_SUMMARY_MINUTE", "0")
    monkeypatch.setenv("STOCK_CHECK_INTERVAL_MINUTES", "30")
    with pytest.raises(ValueError, match="DAILY_SUMMARY_HOUR"):
        load_config()
