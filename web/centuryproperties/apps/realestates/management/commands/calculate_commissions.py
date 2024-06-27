from django.core.management.base import BaseCommand
from django.utils import timezone
from ...models import Payment, Commission


class Command(BaseCommand):
    help = 'Calculate commissions for existing payments'

    def handle(self, *args, **kwargs):
        # Get all approved payments
        payments = Payment.objects.filter(approved=True)

        for payment in payments:
            employee = payment.client.employee
            client = payment.client

            if not employee:
                self.stdout.write(
                    self.style.WARNING(f"Payment {payment.id} does not have an associated employee. Skipping."))
                continue

            # Calculate commission
            commission_amount = payment.amount_paid * 0.1  # Assuming 10% commission

            # Get or create the commission record for the employee and client
            commission, created = Commission.objects.get_or_create(
                employee=employee,
                client=client
            )

            # Update the total commission
            commission.total_commission += commission_amount
            commission.save()

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created commission record for employee {employee.id} and client {client.id}."))
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"Updated commission record for employee {employee.id} and client {client.id}."))

        self.stdout.write(self.style.SUCCESS("Commissions calculation completed."))
