# centuryproperties/realestates/management/commands/expire_clients.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime, time
from ...models import Client, Employees


class Command(BaseCommand):
    help = 'Expire clients and assign them to the administrator'

    def handle(self, *args, **kwargs):

        try:
            admin = Employees.objects.filter(is_administrator=True).first()
        except Employees.DoesNotExist:
            self.stdout.write(self.style.ERROR("Administrator not found."))
            return

        expired_clients = Client.objects.filter(
            client_lands__isnull=True
        )

        for expired_client in expired_clients:
            self.stdout.write(f"Expiring client {expired_client.name} (ID: {expired_client.id})")
            expired_client.employee = admin
            expired_client.save()

        self.stdout.write(self.style.SUCCESS("Expired clients have been reassigned to the administrator."))
