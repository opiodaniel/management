from celery import shared_task
from django.core.management import call_command


@shared_task
def reset_total_amount():
    call_command('reset_total_amount')


@shared_task
def remove_inactive_clients():
    call_command('remove_inactive_clients')


@shared_task
def reset_total_monthly_amount():
    call_command('reset_total_monthly_amount')