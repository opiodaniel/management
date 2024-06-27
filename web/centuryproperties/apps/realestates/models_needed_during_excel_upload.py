from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from datetime import timedelta, datetime, date
from django.core.validators import MinLengthValidator
from django.db.models import Sum
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import connection


class TruncateTableMixin:
    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute(f'TRUNCATE TABLE "{cls._meta.db_table}" RESTART IDENTITY CASCADE')


class Company(TruncateTableMixin, models.Model):
    company_name = models.CharField(max_length=50, default='', blank=True)
    company_logo = models.ImageField(upload_to='company_logo/', blank=True, null=True,
                                     default='company_logo/default_company_logo/default_company_logo.jpeg')
    company_phone_number = models.CharField('phone', max_length=20, default='', blank=True)


class Employees(TruncateTableMixin, models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    is_administrator = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    is_confirmed = models.BooleanField(default=True)

    short_bio = RichTextUploadingField('short_bio', blank=True, null=True)
    bio = RichTextUploadingField('bio', blank=True, null=True)
    #
    address = models.CharField('address', max_length=128, default='', blank=True)
    zip = models.CharField('zip', max_length=20, default='', blank=True)
    city = models.CharField('city', max_length=100, default='', blank=True)
    country = models.CharField('country', max_length=100, default='', blank=True)
    #
    phone = models.CharField('phone', max_length=20, default='', blank=True)
    # date format, 1998-12-28
    date_of_birth = models.DateField(blank=True, null=True)

    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True,
                                    default='profile_pics/default_profile_pic/default.jpg')

    def calculate_weekly_commission(self):
        total_commission = 0

        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())  # Monday of the current week
        end_of_week = start_of_week + timedelta(days=6)  # Sunday of the current week
        print(start_of_week, end_of_week)

        clients = Payment.objects.filter(
            client_landclientemployee=self,
            approved=True,
            timestamp__range=[start_of_week, end_of_week]
        ).order_by('timestamp')

        if clients.exists():
            for client in clients:
                total_commission += client.amount_paid * 0.1  # 10% commission for bringing a client

        return total_commission

    def calculate_commission_from_client(self, client_id):
        try:
            commission = Commission.objects.get(employee=self, client_id=client_id)
            return commission.total_commission
        except Commission.DoesNotExist:
            return 0

    def total_clients(self):
        return Client.objects.filter(employee=self).count()

    def total_approved_clients(self):
        return Payment.objects.filter(client_landclientemployee=self, approved=True).count()

    def total_appending_clients(self):
        return Payment.objects.filter(client_landclientemployee=self, approved=False).count()

    @classmethod
    def total_approved_clients_for_all_employee(cls):
        return sum(employee.total_approved_clients() for employee in cls.objects.all())

    @classmethod
    def total_appending_clients_for_all_employee(cls):
        return sum(employee.total_appending_clients() for employee in cls.objects.all())

    def str(self):
        return self.user.get_full_name()


# @receiver(post_save, sender=User)
# def create_employee(sender, instance, created, **kwargs):
#     if created:
#         Employees.objects.create(user=instance, id=instance.id)

# @receiver(post_save, sender=User)
# def save_employee(sender, instance, **kwargs):
#     instance.employee.save()


class Client(TruncateTableMixin, models.Model):
    name = models.CharField(max_length=100)
    phoneNumber1 = models.CharField(max_length=15, blank=True, default='', validators=[MinLengthValidator(7)])
    phoneNumber2 = models.CharField(max_length=15, blank=True, default='', null=True)
    location = models.CharField(max_length=30, default='', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, null=True)
    employee = models.ForeignKey(Employees, on_delete=models.SET_NULL, null=True, related_name="clients")

    def str(self):
        return self.name


class Land(TruncateTableMixin, models.Model):
    plot_number = models.CharField(max_length=255, blank=True, default='')
    location = models.CharField(max_length=255)
    price = models.IntegerField(default=0)
    available = models.BooleanField(default=True)

    def str(self):
        return self.plot_number


class ClientLand(TruncateTableMixin, models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_lands')
    land = models.ForeignKey(Land, on_delete=models.CASCADE, related_name='client_lands')
    purchase_date = models.DateField(null=True)
    total_installments = models.PositiveIntegerField(default=0)
    total_amount_paid = models.IntegerField(default=0)
    remaining_amount = models.IntegerField(default=0)
    payment_complete = models.BooleanField(default=False)

    def str(self):
        return f'{self.client.name} - {self.land.plot_number}'

    def check_payment_status(self):
        if self.total_amount_paid > 0:
            self.land.available = False
            self.land.save()
        if self.total_amount_paid >= self.land.price:
            self.payment_complete = True
            self.save()


class Payment(TruncateTableMixin, models.Model):
    client_land = models.ForeignKey(ClientLand, on_delete=models.CASCADE, related_name='payments', null=True)
    amount_paid = models.IntegerField(default=0)
    total_amount = models.IntegerField(default=0)
    remaining_amount = models.IntegerField(default=0)
    installment_number = models.PositiveIntegerField(default=1)
    total_installments = models.PositiveIntegerField(default=1)
    installment_date = models.DateField(auto_now_add=True, null=True)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='approved_payments', null=True)
    employee = models.ForeignKey(Employees, on_delete=models.SET_NULL, related_name='employee_payments', null=True)
    timestamp = models.DateField(null=True)

    def str(self):
        return f'{self.client_land.client.name} - {self.client_land.land.plot_number}'

    def save(self, *args, **kwargs):
        if self.pk:  # Check if this is an update
            old_instance = Payment.objects.get(pk=self.pk)
            print('old_instance.amount_paid==', old_instance.amount_paid)
            amount_diff = self.amount_paid
            # amount_diff = self.amount_paid - old_instance.amount_paid
            print('update/edit part amount_diff==', amount_diff)
        else:
            amount_diff = self.amount_paid
            print('Noooo part amount_diff==', amount_diff)

        super().save(*args, **kwargs)

        client_land = self.client_land
        client_land.total_amount_paid = amount_diff  # === don't incude plus sign when uploading excel file =====
        client_land.remaining_amount = client_land.land.price - client_land.total_amount_paid
        client_land.check_payment_status()
        client_land.purchase_date = self.timestamp
        client_land.save()

# def save(self, *args, **kwargs):
#     super().save(*args, **kwargs)
#     client_land = self.client_land
#     client_land.total_amount_paid += self.amount_paid  # === don't incude plus sign when uploading excel file =====
#     client_land.remaining_amount = client_land.land.price - client_land.total_amount_paid
#     client_land.check_payment_status()
#     client_land.purchase_date = self.timestamp
#     client_land.save()


class Commission(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='commissions', null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='commissions', null=True)
    total_commission = models.IntegerField(default=0)
    date_paid = models.DateField(null=True)

    class Meta:
        unique_together = ('employee', 'client')

    def str(self):
        return f"Commission for {self.employee.user.username} from {self.client.name}: {self.total_commission}"


# @receiver(post_save, sender=Payment)
# def update_commission(sender, instance, **kwargs):
#     if instance.approved:
#         commission, created = Commission.objects.get_or_create(
#             employee=instance.client_land.client.employee,
#             client=instance.client_land.client,
#             defaults={'date_paid': instance.timestamp, 'total_commission': 0}
#         )
#
#         new_commission = instance.amount_paid * 0.1
#         # print('=====new_commission=======', new_commission)
#         commission.total_commission += new_commission  # === don't incude plus sign when uploading excel file =====
#         commission.date_paid = instance.timestamp
#         commission.save()


@receiver(post_save, sender=Payment)
def update_commission(sender, instance, **kwargs):
    if instance.approved:
        commission, created = Commission.objects.get_or_create(
            employee=instance.client_land.client.employee,
            client=instance.client_land.client,
            defaults={'date_paid': instance.timestamp, 'total_commission': 0}
        )

        if instance.pk:  # Check if this is an update
            old_instance = Payment.objects.get(pk=instance.pk)
            amount_diff = instance.amount_paid
        # amount_diff = instance.amount_paid - old_instance.amount_paid
        else:
            amount_diff = instance.amount_paid

        new_commission = amount_diff * 0.1
        commission.total_commission = new_commission  # === don't incude plus sign when uploading excel file =====
        commission.date_paid = instance.timestamp
        commission.save()


class EmployeePaymentRecord(TruncateTableMixin, models.Model):
    total_commission = models.IntegerField(default=0)
    amount_paid = models.IntegerField(default=0)
    balance = models.IntegerField(default=0)
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE,
                                 related_name='employee_employeepaymenrecord', null=True)


# @receiver(post_save, sender=Employees)
# def create_employee_payment_record(sender, instance, created, **kwargs):
#     if created:
#         if not instance.user.is_superuser:
#             EmployeePaymentRecord.objects.create(employee=instance, id=instance.id)

