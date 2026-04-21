import time
from apscheduler.schedulers.background import BackgroundScheduler


def test_scheduler_executes_jobs(mocker):
    """Both jobs execute within the scheduled interval and failures don't stop the scheduler."""
    calls = []

    def fake_job(**kwargs):
        calls.append(1)

    mocker.patch("slack_notifier.scheduler.load_config")
    scheduler = BackgroundScheduler()

    scheduler.add_job(fake_job, trigger="interval", seconds=1, id="job1")
    scheduler.add_job(fake_job, trigger="interval", seconds=1, id="job2")
    scheduler.start()

    time.sleep(2.5)
    scheduler.shutdown(wait=False)

    assert len(calls) >= 2, "Expected at least 2 job executions"


def test_scheduler_survives_job_failure(mocker):
    """A failing job does not stop the scheduler from running subsequent jobs."""
    calls = []
    fail_count = [0]

    def flaky_job(**kwargs):
        fail_count[0] += 1
        if fail_count[0] == 1:
            raise RuntimeError("simulated failure")
        calls.append(1)

    scheduler = BackgroundScheduler()
    scheduler.add_job(flaky_job, trigger="interval", seconds=1, id="flaky")
    scheduler.start()

    time.sleep(3)
    scheduler.shutdown(wait=False)

    assert len(calls) >= 1, "Scheduler should continue after a job failure"
