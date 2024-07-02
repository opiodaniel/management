from celery import shared_task
from django.core.management import call_command

# tasks.py

from celery import shared_task
from datetime import datetime, timedelta
from django.core.mail import EmailMessage
from django.conf import settings
import os
import pandas as pd
from .models import Client, Employees


@shared_task
def expire_clients():
    call_command('expire_clients')



