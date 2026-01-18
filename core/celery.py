import os
from celery import Celery

# Mental model (clean version)
# Step A: Ensure Django settings can be loaded (DJANGO_SETTINGS_MODULE).
# Step B: Create Celery app (Celery("core")).
# Step C: Load Celery config from Django settings (CELERY_* keys).
# Step D: Discover task modules across installed Django apps (autodiscover_tasks()).
# Step E: When you run a worker, it connects to the broker (CELERY_BROKER_URL) and starts consuming tasks.

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# core/celery.py or wherever you configure Celery
from celery.schedules import crontab
app.conf.beat_schedule = {
    "purge-expired-license-downloads": {
        "task": "licenses.tasks.purge_expired_license_downloads",
        "schedule": crontab(minute=0, hour="*/6"),
    }
}