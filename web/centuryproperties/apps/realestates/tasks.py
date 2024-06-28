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
def reset_total_amount():
    call_command('reset_total_amount')


@shared_task
def remove_inactive_clients():
    call_command('remove_inactive_clients')


@shared_task
def reset_total_monthly_amount():
    call_command('reset_total_monthly_amount')


@shared_task
def free_old_clients():
    one_week_ago = datetime.now() - timedelta(days=7)
    old_clients = Client.objects.filter(date_joined__lte=one_week_ago, employee__isnull=False)

    # Update clients to be free
    old_clients.update(employee=None)

    # Generate Excel file
    client_data = old_clients.values('id', 'name', 'email', 'phone')
    df = pd.DataFrame(list(client_data))
    excel_file_path = os.path.join(settings.MEDIA_ROOT, 'free_clients.xlsx')
    df.to_excel(excel_file_path, index=False)

    # Send email with Excel file
    email = EmailMessage(
        'List of Free Clients',
        'Attached is the list of clients who are now free.',
        settings.DEFAULT_FROM_EMAIL,
        ['recipient@example.com'],  # Replace with actual recipient
    )
    email.attach_file(excel_file_path)
    email.send()

    # Alternatively, save the file and make it available for download
    # Implement as per your requirement
