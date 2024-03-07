from datetime import datetime
from django.core.management.base import BaseCommand
from ...models import MonthlyTotal
from datetime import timedelta
from datetime import date


class Command(BaseCommand):
    help = 'Reset the total amount to zero at the beginning of each month'

    def handle(self, *args, **options):
        # # Get the current date
        # today = datetime.now().date()
        #
        # # Set the current date to the first day of the month
        # current_month = today.replace(day=1)
        #
        # # Check if there's a record for the current month
        # try:
        #     monthly_total = MonthlyTotal.objects.get(month=current_month)
        # except MonthlyTotal.DoesNotExist:
        #     # If not, create a new record for the current month with amount set to zero
        #     monthly_total = MonthlyTotal.objects.create(month=current_month, amount=0)
        #
        # # Reset the amount to zero
        # monthly_total.amount = 0
        # monthly_total.save()

        # # Get the current date
        # today = datetime.now().date()
        # # Set the start date (assuming you want to start from January of a particular year)
        # start_date = datetime(today.year, 1, 1).date()
        #
        # # Loop through each month from the start date up to the current month
        # current_date = start_date
        # while current_date <= today:
        #     # Get the first day of the current month
        #     first_day_of_month = datetime(current_date.year, current_date.month, 1).date()
        #
        #     # Check if a record already exists for the current month
        #     if not MonthlyTotal.objects.filter(month=first_day_of_month).exists():
        #         # If not, create a new record with the amount set to zero
        #         MonthlyTotal.objects.create(month=first_day_of_month, amount=0)
        #
        #     # Move to the next month
        #     current_date = first_day_of_month + timedelta(days=32)  # Move to the next month's first day

        # # Get the current date
        # today = datetime.now().date()
        #
        # # Set the start date (assuming you want to start from January of a particular year)
        # start_date = datetime(today.year, 1, 1).date()
        #
        # # Loop through each month from the start date up to the current month
        # current_date = start_date
        # while current_date <= today:
        #     # Get the first day of the current month
        #     first_day_of_month = datetime(current_date.year, current_date.month, 1).date()
        #
        #     # Check if a record already exists for the current month
        #     monthly_total, created = MonthlyTotal.objects.get_or_create(month=first_day_of_month)
        #
        #     # Reset the amount field to zero
        #     monthly_total.amount = 0
        #     monthly_total.save()
        #
        #     # Move to the next month
        #     current_date = first_day_of_month + timedelta(days=32)  # Move to the next month's first day

        # Get the current date
        today = datetime.now().date()

        # Set the start date to the beginning of the current month
        start_of_month = today.replace(day=1)

        # Check if a MonthlyTotal object exists for the current month
        monthly_total_obj, created = MonthlyTotal.objects.get_or_create(month=start_of_month)

        # Reset the total amount to zero
        monthly_total_obj.amount = 0
        monthly_total_obj.save()

        self.stdout.write(self.style.SUCCESS('Amount successfully set to zero for the new month.'))