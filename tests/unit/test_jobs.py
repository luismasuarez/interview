from datetime import date, timedelta
from unittest.mock import patch, MagicMock
from slack_notifier.jobs import daily_summary_job, stock_alert_job


DB_URL = "sqlite:///./test.db"
WEBHOOK = "https://hooks.slack.com/test"
YESTERDAY = date.today() - timedelta(days=1)
DATE_STR = YESTERDAY.strftime("%d/%m/%Y")


# --- daily_summary_job ---

def test_daily_summary_with_orders(mocker):
    rows = [
        {"buyer_name": "Ana", "product_name": "Widget", "total_qty": 3},
        {"buyer_name": "Ana", "product_name": "Gadget", "total_qty": 1},
        {"buyer_name": "Bob", "product_name": "Widget", "total_qty": 2},
    ]
    mocker.patch("slack_notifier.jobs.db.get_daily_summary", return_value=rows)
    mock_send = mocker.patch("slack_notifier.jobs.slack.send_message")

    daily_summary_job(DB_URL, WEBHOOK)

    mock_send.assert_called_once()
    text = mock_send.call_args[0][1]
    assert DATE_STR in text
    assert "Ana" in text
    assert "Bob" in text
    assert "Widget x3" in text
    assert "📊" in text


def test_daily_summary_no_orders(mocker):
    mocker.patch("slack_notifier.jobs.db.get_daily_summary", return_value=[])
    mock_send = mocker.patch("slack_notifier.jobs.slack.send_message")

    daily_summary_job(DB_URL, WEBHOOK)

    mock_send.assert_called_once()
    assert "Sin compras" in mock_send.call_args[0][1]


def test_daily_summary_db_error_no_slack(mocker):
    mocker.patch("slack_notifier.jobs.db.get_daily_summary", side_effect=Exception("DB down"))
    mock_send = mocker.patch("slack_notifier.jobs.slack.send_message")

    daily_summary_job(DB_URL, WEBHOOK)

    mock_send.assert_not_called()


# --- stock_alert_job ---

def test_stock_alert_sends_when_below_threshold(mocker):
    products = [{"name": "Widget", "stock": 2, "min_stock": 10}]
    mocker.patch("slack_notifier.jobs.db.get_low_stock_products", return_value=products)
    mock_send = mocker.patch("slack_notifier.jobs.slack.send_message")

    stock_alert_job(DB_URL, WEBHOOK)

    mock_send.assert_called_once()
    text = mock_send.call_args[0][1]
    assert "Widget" in text
    assert "2 unidades" in text
    assert "mínimo: 10" in text
    assert "⚠️" in text


def test_stock_alert_no_message_when_all_ok(mocker):
    mocker.patch("slack_notifier.jobs.db.get_low_stock_products", return_value=[])
    mock_send = mocker.patch("slack_notifier.jobs.slack.send_message")

    stock_alert_job(DB_URL, WEBHOOK)

    mock_send.assert_not_called()


def test_stock_alert_db_error_no_slack(mocker):
    mocker.patch("slack_notifier.jobs.db.get_low_stock_products", side_effect=Exception("DB down"))
    mock_send = mocker.patch("slack_notifier.jobs.slack.send_message")

    stock_alert_job(DB_URL, WEBHOOK)

    mock_send.assert_not_called()
