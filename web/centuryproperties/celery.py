from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centuryproperties.settings.dev')

app = Celery('centuryproperties')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'expire_clients': {
        'task': 'realestates.tasks.expire_clients',
        'schedule': crontab(hour=10, minute=35),  # Adjust this to a few minutes ahead of the current time for testing
    },
}
