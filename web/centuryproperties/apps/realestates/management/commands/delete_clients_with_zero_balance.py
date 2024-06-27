from django.core.management.base import BaseCommand
from django.db.models.signals import post_save
from ...models import Payment, Client, Employees, update_commission


class Command(BaseCommand):
    help = 'Delete clients with approved payments and zero balance'

    def handle(self, *args, **kwargs):
        # Disconnect the update_commission signal
        post_save.disconnect(update_commission, sender=Payment)

        try:
            # Get all employees
            employees = Employees.objects.all()

            for employee in employees:
                self.stdout.write(f"Processing employee {employee.user.get_full_name()} (ID: {employee.id})")

                # Get all clients for the current employee
                clients = employee.client_employee.all()

                for client in clients:
                    payments = client.client_payment.all()
                    self.stdout.write(f"Checking client {client.name} (ID: {client.id}). Payments count: {payments.count()}")

                    if payments.exists() and all(payment.approved and payment.remaining_amount == 0 for payment in payments):
                        self.stdout.write(f"Deleting client {client.name} (ID: {client.id})")
                        client.delete()
                    else:
                        self.stdout.write(f"Client {client.name} (ID: {client.id}) does not meet the criteria for deletion.")

            self.stdout.write(self.style.SUCCESS("Client deletion process completed."))
        finally:
            # Reconnect the update_commission signal
            post_save.connect(update_commission, sender=Payment)
