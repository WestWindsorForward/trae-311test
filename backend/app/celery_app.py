import os
from celery import Celery

broker_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("township311", broker=broker_url, backend=broker_url)
celery_app.conf.timezone = "UTC"
celery_app.conf.beat_schedule = {
    "weekly-report": {
        "task": "app.tasks.reports.weekly_report",
        "schedule": 7 * 24 * 60 * 60,
    }
}

@celery_app.task(name="app.tasks.ai.ai_triage_task")
def ai_triage_task(payload: dict) -> dict:
    from app.tasks.ai import triage
    return triage(payload)

@celery_app.task(name="app.tasks.reports.weekly_report")
def weekly_report():
    from app.tasks.reports import generate_weekly_report
    return generate_weekly_report()
