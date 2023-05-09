"""
Celery configuration with REDIS broker.
"""

import os
from celery import Celery

from .base_settings import SETTINGS_FILE


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_FILE)

# Create app instance
app = Celery("brandishseo")

# All celery-related configuration keys should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.broker_url = os.environ.get("REDIS_URL", "redis://localhost:6379")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
