from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth.models import User
from ...models import Employees, Client, Land, ClientLand, Payment, Commission

class Command(BaseCommand):
    help = 'Truncate all data from the database, including users'

    def handle(self, *args, **kwargs):
        # List all the tables you want to truncate
        tables = [
            Commission._meta.db_table,
            Payment._meta.db_table,
            ClientLand._meta.db_table,
            Land._meta.db_table,
            Client._meta.db_table,
            Employees._meta.db_table,
            User._meta.db_table,
        ]

        with connection.cursor() as cursor:
            for table in tables:
                cursor.execute(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE;')
                self.stdout.write(self.style.SUCCESS(f'Successfully truncated {table}'))

        self.stdout.write(self.style.SUCCESS('Successfully truncated all data from the database'))
