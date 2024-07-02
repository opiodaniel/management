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
        'task': 'centuryproperties.apps.realestates.tasks.expire_clients',
        'schedule': crontab(hour=0, minute=0, day_of_week='sunday'),
    },
}

# Testing:
# celery -A centuryproperties worker --loglevel=info
# celery -A centuryproperties beat --loglevel=info
