import time
import pytest
import requests
from unittest.mock import patch, MagicMock
from slack_notifier.slack import send_message


WEBHOOK = "https://hooks.slack.com/test"


def test_send_message_success(mocker):
    mock_post = mocker.patch("slack_notifier.slack.requests.post")
    mock_post.return_value.status_code = 200

    send_message(WEBHOOK, "hello")

    mock_post.assert_called_once_with(WEBHOOK, json={"text": "hello"}, timeout=10)


def test_send_message_retries_on_failure(mocker):
    mock_post = mocker.patch("slack_notifier.slack.requests.post")
    mock_post.return_value.status_code = 500
    mock_post.return_value.text = "error"
    mocker.patch("slack_notifier.slack.time.sleep")  # skip 30s wait

    send_message(WEBHOOK, "hello")

    assert mock_post.call_count == 2


def test_send_message_succeeds_on_second_attempt(mocker):
    mock_post = mocker.patch("slack_notifier.slack.requests.post")
    fail = MagicMock(status_code=500, text="error")
    ok = MagicMock(status_code=200)
    mock_post.side_effect = [fail, ok]
    mocker.patch("slack_notifier.slack.time.sleep")

    send_message(WEBHOOK, "hello")

    assert mock_post.call_count == 2


def test_send_message_handles_request_exception(mocker):
    mock_post = mocker.patch("slack_notifier.slack.requests.post",
                             side_effect=requests.RequestException("timeout"))
    mocker.patch("slack_notifier.slack.time.sleep")

    send_message(WEBHOOK, "hello")  # should not raise

    assert mock_post.call_count == 2
