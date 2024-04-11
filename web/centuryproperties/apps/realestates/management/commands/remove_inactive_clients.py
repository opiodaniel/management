# management/commands/remove_inactive_clients.py
from django.core.management.base import BaseCommand
from datetime import timedelta
from django.utils import timezone
from ...models import Client


class Command(BaseCommand):
    help = 'Remove inactive clients who haven\'t made a payment within a certain period of time'

    def handle(self, *args, **kwargs):
        # Calculate the cutoff date (e.g., clients who haven't made a payment in the last 30 days)
        cutoff_date = timezone.now() - timedelta(days=7)

        print('===inside commands cutoff_date===', cutoff_date)

        # Filter clients who have been inactive (appending) for more than 30 days
        inactive_clients = Client.objects.filter(
            client_payment__approved=False,  # Not approved by the admin
            date__lt=cutoff_date  # Registration date older than cutoff date
        )
        print('===inactive_clients==', inactive_clients)
        # Delete inactive clients
        # inactive_clients.delete()

        self.stdout.write(self.style.SUCCESS('Inactive clients removed successfully.'))
