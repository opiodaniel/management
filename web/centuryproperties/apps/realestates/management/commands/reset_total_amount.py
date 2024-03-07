# management/commands/reset_total_amount.py

from django.core.management.base import BaseCommand
from ...models import TotalAmount
from datetime import datetime


class Command(BaseCommand):
    help = 'Reset the total amount to zero at the beginning of each day'

    def handle(self, *args, **options):
        # Get today's date
        today = datetime.now().date()
        print(today)

        # Check if a TotalAmount object exists for today
        total_amount_obj, created = TotalAmount.objects.get_or_create(date=today)

        # Reset the total amount to zero
        total_amount_obj.amount = 0
        total_amount_obj.save()

        self.stdout.write(self.style.SUCCESS('Total amount reset successfully for today.'))
