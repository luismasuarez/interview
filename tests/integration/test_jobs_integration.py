from datetime import date, timedelta
from sqlalchemy import create_engine, text
from slack_notifier.jobs import daily_summary_job, stock_alert_job

WEBHOOK = "https://hooks.slack.com/test"


def _make_db():
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                stock INTEGER NOT NULL,
                min_stock INTEGER
            )
        """))
        conn.execute(text("""
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                buyer_name TEXT NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                order_date DATE NOT NULL
            )
        """))
        conn.commit()
    return engine


def test_daily_summary_integration(mocker):
    engine = _make_db()
    yesterday = date.today() - timedelta(days=1)

    with engine.connect() as conn:
        conn.execute(text("INSERT INTO products VALUES (1, 'Widget', 50, 10)"))
        conn.execute(text(
            f"INSERT INTO orders VALUES (1, 'Ana', 1, 3, '{yesterday}')"
        ))
        conn.commit()

    mock_send = mocker.patch("slack_notifier.jobs.slack.send_message")

    # Patch create_engine to return our in-memory engine
    mocker.patch("slack_notifier.db.create_engine", return_value=engine)

    daily_summary_job("sqlite:///:memory:", WEBHOOK)

    mock_send.assert_called_once()
    text_sent = mock_send.call_args[0][1]
    assert "Ana" in text_sent
    assert "Widget" in text_sent


def test_stock_alert_integration(mocker):
    engine = _make_db()

    with engine.connect() as conn:
        conn.execute(text("INSERT INTO products VALUES (1, 'Widget', 2, 10)"))
        conn.commit()

    mock_send = mocker.patch("slack_notifier.jobs.slack.send_message")
    mocker.patch("slack_notifier.db.create_engine", return_value=engine)

    stock_alert_job("sqlite:///:memory:", WEBHOOK)

    mock_send.assert_called_once()
    assert "Widget" in mock_send.call_args[0][1]
