from django.core.management.base import BaseCommand
from django.utils import timezone
from ...models import Client, ClientLand, Payment


class Command(BaseCommand):
    help = 'Retrieve clients with approved payments and remaining amount less than zero, including associated employees'

    def handle(self, *args, **kwargs):
        # Get all ClientLand records with remaining amount less than zero
        client_lands = ClientLand.objects.filter(remaining_amount__lt=0)

        # Dictionary to store clients and their associated employees
        client_employee_map = {}

        for client_land in client_lands:
            client = client_land.client
            employee = client.employee

            # Ensure the client and employee are valid
            if not client:
                self.stdout.write(self.style.WARNING(f"ClientLand {client_land.id} does not have an associated client. Skipping."))
                continue

            if not employee:
                self.stdout.write(self.style.WARNING(f"Client {client.id} does not have an associated employee. Skipping."))
                continue

            # Add client and employee to the dictionary
            if client.id not in client_employee_map:
                client_employee_map[client.id] = {
                    'client': client,
                    'employees': set()
                }

            client_employee_map[client.id]['employees'].add(employee)

        # Display the clients and their associated employees
        for client_id, data in client_employee_map.items():
            client = data['client']
            employees = data['employees']
            self.stdout.write(self.style.SUCCESS(f"Client: {client.name} (ID: {client.id})"))
            for employee in employees:
                self.stdout.write(f"  - Employee: (fullName: {employee.user.get_full_name()}) (user_name: {employee.user.username}) (ID: {employee.id})")

        self.stdout.write(self.style.SUCCESS("Client and employee retrieval completed."))

