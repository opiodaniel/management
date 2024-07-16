from django.core.management.base import BaseCommand
from django.db.models import Count
from ...models import Client, Employees


class Command(BaseCommand):
    help = 'Retrieve duplicate clients with the same phone number and their employees'

    def handle(self, *args, **kwargs):
        # Identify duplicate phone numbers in phoneNumber1
        duplicate_phone_numbers = Client.objects.values('phoneNumber1').annotate(
            count=Count('phoneNumber1')).filter(count__gt=1).values_list('phoneNumber1', flat=True)

        # Retrieve clients with duplicate phone numbers
        duplicate_clients = Client.objects.filter(phoneNumber1__in=duplicate_phone_numbers).order_by('phoneNumber1')

        # Group duplicate clients by phone number
        duplicates_by_phone = {}
        for client in duplicate_clients:
            phone_number = client.phoneNumber1
            if phone_number not in duplicates_by_phone:
                duplicates_by_phone[phone_number] = []
            duplicates_by_phone[phone_number].append(client)

        # Print the duplicate clients and their associated employees
        for phone_number, clients in duplicates_by_phone.items():
            self.stdout.write(f"Phone Number: {phone_number}")
            for client in clients:
                employee_name = client.employee.user.username if client.employee else 'Unknown Employee'
                self.stdout.write(f"    Client: {client.name} (ID: {client.id}), Entered by: {employee_name}")

        self.stdout.write(self.style.SUCCESS("Retrieved duplicate clients with their employees."))

