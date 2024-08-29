from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from ...models import Client, Employees


class Command(BaseCommand):
    help = 'Generate expiry dates for expired clients who belong to the admin'

    def handle(self, *args, **kwargs):
        try:
            admin = Employees.objects.filter(is_administrator=True).last()
        except Employees.DoesNotExist:
            self.stdout.write(self.style.ERROR("Administrator not found."))
            return

        # Fetch expired clients assigned to the admin
        expired_clients = Client.objects.filter(employee=admin, expired_date__isnull=True)

        if not expired_clients.exists():
            self.stdout.write(self.style.WARNING("No expired clients found for the admin."))
            return

        total_clients = expired_clients.count()
        self.stdout.write(f"Found {total_clients} expired clients for the admin.")

        # Define a range for expiry dates (e.g., next 30 days)
        start_date = timezone.now() - timedelta(days=30)
        print(start_date)
        end_date = start_date + timedelta(days=30)
        print(end_date)
        date_range = (end_date - start_date).days
        print(date_range)

        # Assign expiry dates
        for idx, client in enumerate(expired_clients):
            # Distribute expiry dates within the defined range
            expiry_date = start_date + timedelta(days=(idx % date_range))
            client.expired_date = expiry_date
            client.save()
            self.stdout.write(f"Assigned expiry date {expiry_date.strftime('%Y-%m-%d')} to client {client.name} (ID: {client.id})")

        self.stdout.write(self.style.SUCCESS("Expiry dates have been assigned to all expired clients for the admin."))
