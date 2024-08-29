from django.core.management.base import BaseCommand
import openpyxl
from datetime import timedelta, datetime, time
from django.utils import timezone
from ...models import Client, Employees


class Command(BaseCommand):
    help = 'Expire clients and assign them to the administrator'

    def handle(self, *args, **kwargs):

        try:
            admin = Employees.objects.filter(is_administrator=True).first()
        except Employees.DoesNotExist:
            self.stdout.write(self.style.ERROR("Administrator not found."))
            return
        # Load the Excel file with clients who expired last Sunday
        # /home/centuryproperties/management/web/centuryproperties/apps/realestates/management/
        excel_file_path = '/home/opio/projects/management/web/centuryproperties/apps/realestates/management/commands/12-latest-download.xlsx'  # Update this with the actual path
        workbook = openpyxl.load_workbook(excel_file_path)
        sheet = workbook.active

        # Extract the phone numbers of clients who expired last Sunday
        expired_last_week_contacts = set()
        for row in sheet.iter_rows(min_row=2, values_only=True):  # Skipping the header row
            name, contact = row
            expired_last_week_contacts.add(contact)

        expired_clients = Client.objects.filter(
            client_lands__isnull=True,
            employee=admin
        ).exclude(employee__exclude_from_reassignment=True)

        one_week_ago = timezone.now() - timedelta(days=8)
        yesterday = timezone.now() - timedelta(days=1)

        for expired_client in expired_clients:
            self.stdout.write(f"Checking client {expired_client.name} (ID: {expired_client.id})")
            if expired_client.phoneNumber1 in expired_last_week_contacts:
                self.stdout.write(f"Client {expired_client.name} (ID: {expired_client.id}) expired last week")
                expired_client.expired_date = one_week_ago  # Last Sunday
            else:
                self.stdout.write(f"Client {expired_client.name} (ID: {expired_client.id}) expired yesterday")
                expired_client.expired_date = yesterday  # Yesterday
            expired_client.save()

        self.stdout.write(self.style.SUCCESS("Expired clients have been reassigned to the administrator."))
