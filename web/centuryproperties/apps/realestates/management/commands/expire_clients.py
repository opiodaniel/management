# centuryproperties/realestates/management/commands/expire_clients.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime, time
from centuryproperties.apps.realestates.models import Client, Employees


class Command(BaseCommand):
    help = 'Expire clients and assign them to the administrator'

    def handle(self, *args, **kwargs):

        try:
            admin = Employees.objects.filter(is_administrator=True).last()
        except Employees.DoesNotExist:
            self.stdout.write(self.style.ERROR("Administrator not found."))
            return

        expiration_date = timezone.now() - timedelta(days=7)

        expired_clients = Client.objects.filter(
            date__lt=expiration_date,
            client_lands__isnull=True,
            is_archived=False,
        ).exclude(employee__exclude_from_reassignment=True).exclude(employee=admin)


        # print(expired_clients)

        for expired_client in expired_clients:
            self.stdout.write(f"Expiring client {expired_client.name} (ID: {expired_client.id})")
            expired_client.employee = admin
            expired_client.expired_date = timezone.now()
            expired_client.save()

        self.stdout.write(self.style.SUCCESS("Expired clients have been reassigned to the administrator."))

# from django.core.management.base import BaseCommand
# from django.utils import timezone
# from datetime import timedelta, datetime, time
# from ...models import Client, Employees
#
#
#
# class Command(BaseCommand):
#     help = 'Expire clients and assign them to the administrator'
#
#     def handle(self, *args, **kwargs):
#
#         try:
#             admin = Employees.objects.filter(is_administrator=True).last()
#         except Employees.DoesNotExist:
#             self.stdout.write(self.style.ERROR("Administrator not found."))
#             return
#
#         expired_clients = Client.objects.filter(
#             client_lands__isnull=True
#         ).exclude(employee__exclude_from_reassignment=True).exclude(employee=admin)
#
#         for expired_client in expired_clients:
#             self.stdout.write(f"Expiring client {expired_client.name} (ID: {expired_client.id})")
#             expired_client.employee = admin
#             expired_client.expired_date = timezone.now()
#             expired_client.save()
#
#         self.stdout.write(self.style.SUCCESS("Expired clients have been reassigned to the administrator."))



# class Command(BaseCommand):
#     help = 'Expire clients and assign them to the administrator'
#
#     def handle(self, *args, **kwargs):
#
#         try:
#             admin = Employees.objects.filter(is_administrator=True).last()
#         except Employees.DoesNotExist:
#             self.stdout.write(self.style.ERROR("Administrator not found."))
#             return
#
#         expiration_date = timezone.now() - timedelta(days=7)
#
#         expired_clients = Client.objects.filter(
#             date__lt=expiration_date,
#             client_lands__isnull=True
#         ).exclude(employee__exclude_from_reassignment=True).exclude(employee=admin)
#
#         for expired_client in expired_clients:
#             self.stdout.write(f"Expiring client {expired_client.name} (ID: {expired_client.id})")
#             expired_client.employee = admin
#             expired_client.expired_date = timezone.now()
#             expired_client.save()
#
#         self.stdout.write(self.style.SUCCESS("Expired clients have been reassigned to the administrator."))
