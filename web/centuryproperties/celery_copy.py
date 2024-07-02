from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings
from datetime import datetime

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centuryproperties.settings.dev')

# Create a Celery instance.
app = Celery('centuryproperties')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks in all installed apps.
app.autodiscover_tasks()

# Run to automatically update the totalamount

# celery -A management worker --loglevel=info
# celery -A management beat --loglevel=info


app = Celery('centuryproperties')

# Other Celery configurations...

# Schedule the management command to run daily
app.conf.beat_schedule = {
    'remove-inactive-clients': {
        'task': 'centuryproperties.realestates.tasks.remove_inactive_clients',
        'schedule': crontab(hour=0, minute=0),  # Run at midnight every day
    },
}

app.conf.beat_schedule = {
    'reset-monthly-total': {
        'task': 'centuryproperties.realestates.tasks.reset_total_monthly_amount',
        'schedule': crontab(day_of_month=1, hour=0, minute=0),  # Run at 00:00 on the 1st day of each month
    },
}


app.conf.beat_schedule = {
    'reset-total-amount': {
        'task': 'centuryproperties.realestates.tasks.reset_total_amount',
        'schedule': crontab(minute=0, hour=0),  # Run at midnight every day
    },
}

# Get current time
now = datetime.now()

# app.conf.beat_schedule = {
#     'expire_clients': {
#         'task': 'realestates.tasks.expire_clients',
#         'schedule': crontab(minute=(now.minute + 1) % 60, hour=now.hour, day_of_week=now.strftime('%A').lower()),  # Run in 2 minutes from now
#     },
# }

# app.conf.beat_schedule = {
#     'expire_clients': {
#         'task': 'realestates.tasks.expire_clients',
#         'schedule': crontab(minute=50, hour=18, day_of_week='monday'),
#     },
# }

app.conf.beat_schedule = {
    'expire_clients': {
        'task': 'realestates.tasks.expire_clients',
        'schedule': crontab(hour=10, minute=29),
    },
}