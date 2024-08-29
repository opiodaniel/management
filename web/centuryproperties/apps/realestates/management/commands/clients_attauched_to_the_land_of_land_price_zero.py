from django.core.management.base import BaseCommand
from openpyxl import Workbook
from django.utils import timezone
from ...models import Employees, ClientLand


class Command(BaseCommand):
    help = 'Export client and land information to an Excel file then the info is deleted from the database'

    def handle(self, *args, **kwargs):

        # Define the Excel file path//// excel file where info is written in.

        excel_file_path = '/home/opio/projects/management/web/centuryproperties/apps/realestates/management/commands/clients_with_zero_or_less_land_price.xlsx'

        # Filter ClientLand instances with land price zero or less
        client_lands = ClientLand.objects.filter(land__price__lte=0).select_related('client', 'land', 'client__employee')

        # Create a new Excel workbook and sheet
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Client Land Information'

        # Write the header row
        headers = [
            'employee_name', 'user_name', 'user_email', 'employee_contact', 'client_name',
            'client_contact1', 'client_contact2', 'client_location', 'date_client_entered',
            'land_location', 'amount_paid', 'land_price', 'remaining_amount',
            'installment_number', 'total_Installments', 'payment_date', 'payment_approved'
        ]
        sheet.append(headers)

        # Write the data rows
        for client_land in client_lands:
            employee = client_land.client.employee
            client = client_land.client
            land = client_land.land

            row = [
                employee.user.get_full_name(),
                employee.user.username,
                employee.user.email,
                employee.phone,
                client.name,
                client.phoneNumber1,
                client.phoneNumber2,
                '',  # Assuming client_location is not available in the current models
                timezone.now().strftime('%Y-%m-%d %H:%M:%S'),  # Example date_client_entered
                land.location,
                client_land.total_amount_paid,
                land.price,
                client_land.remaining_amount,
                1,  # Assuming installment_number is not available in the current models
                client_land.total_installments,
                client_land.purchase_date.strftime('%Y-%m-%d') if client_land.purchase_date else '',
                int(client_land.payment_complete)
            ]
            sheet.append(row)

        # Save the workbook to the specified file path
        workbook.save(excel_file_path)

        # Delete the records after exporting
        client_lands.delete()

        self.stdout.write(self.style.SUCCESS(f"Client land information exported successfully to {excel_file_path}"))

