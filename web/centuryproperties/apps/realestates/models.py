from django.db import models
from django.contrib.auth.models import User
import datetime
import decimal
from .sql import TruncateTableMixin
from django.db.models.signals import post_save
from django.dispatch import receiver
from ckeditor_uploader.fields import RichTextUploadingField
from datetime import date
from phonenumber_field.modelfields import PhoneNumberField
from datetime import datetime, timedelta
from django.core.validators import MinLengthValidator

class Company(TruncateTableMixin, models.Model):
    company_name = models.CharField(max_length=50, default='', blank=True)
    company_logo = models.ImageField(upload_to='company_logo/', blank=True, null=True,
                                     default='company_logo/default_profile_pic/default_company_logo_.jpg')
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
    date_of_birth = models.DateField(blank=True, null=True)

    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True,
                                    default='profile_pics/default_profile_pic/default.jpg')

    def calculate_weekly_commission(self):
        total_commission = 0

        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())  # Monday of the current week
        end_of_week = start_of_week + timedelta(days=6)  # Sunday of the current week
        print(start_of_week,  end_of_week)
        # Filter the payments made within the current week
        clients = Payment.objects.filter(
            client__employee=self,
            approved=True,
            timestamp__range=[start_of_week, end_of_week]
        ).order_by('timestamp')  # Sort by timestamp to ensure correct or
        # print(clients)

        if clients.exists():
            # Calculate commission for each client
            for client in clients:
                total_commission += client.amount_paid * 0.1  # 10% commission for bringing a client
                # print('alone', total_commission)

            pair_count = len(clients) // 2
            remaining_clients = len(clients) % 2
            pair_commissions = []
            if pair_count > 0:
                amounts_paid = [client.amount_paid for client in clients]
                # print(amounts_paid)
                for i in range(pair_count):
                    pair_minimum_amount = min(amounts_paid[2 * i], amounts_paid[2 * i + 1])  #Take the minimum amount from each pair
                    total_commission += pair_minimum_amount * 0.05  # Additional 5% for every pair
                    pair_commissions.append(total_commission)
            # total_commission += sum(pair_commissions)
            # print('total_pair_commissions  ', total_commission)

            # if len(pair_commissions) > 0:
            #     total_commission = sum(pair_commissions)

            # If there's an odd number of clients, calculate commission for the last client individually
            # if remaining_clients:
            #     if len(clients) % 2 == 1:  # Check if the last client is not part of a pair
            #         total_commission += clients.last().amount_paid * 0.1  # 10% commission for the last client

        return total_commission

    def total_clients(self):
        return self.client_employee.count()

    def total_approved_clients(self):
        return Payment.objects.filter(client__employee=self, approved=True).count()

    def total_appending_clients(self):
        return Payment.objects.filter(client__employee=self, approved=False).count()

    @classmethod
    def total_approved_clients_for_all_employee(cls):
        return sum(employee.client_employee.filter(approved=True).count() for employee in cls.objects.all())

    @classmethod
    def total_appending_clients_for_all_employee(cls):
        return sum(employee.client_employee.filter(approved=False).count() for employee in cls.objects.all())

    def __str__(self):
        return self.user.get_full_name()


@receiver(post_save, sender=User)
def create_employee(sender, instance, created, **kwargs):
    if created:
        Employees.objects.create(user=instance, id=instance.id)


@receiver(post_save, sender=User)
def save_employee(sender, instance, created, **kwargs):
    if created:
        instance.employee.save()


class Client(TruncateTableMixin, models.Model):
    name = models.CharField(max_length=100)
    phoneNumber1 = models.CharField(max_length=10, blank=True, default='', validators=[MinLengthValidator(10)])
    phoneNumber2 = models.CharField(max_length=10, blank=True, default='', null=True)
    location = models.CharField(max_length=30, default='', blank=True, null=True)
    date = models.DateField(auto_now_add=True, null=True)
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name="client_employee")

    def __str__(self):
        return self.name


class Payment(TruncateTableMixin, models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="client_payment")
    amount_paid = models.IntegerField(default=0)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='approved_payments', null=True)
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='employee_payments', null=True)
    timestamp = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Payment for {self.client.name}"


class EmployeePaymentRecord(TruncateTableMixin, models.Model):
    total_commission = models.IntegerField(default=0)
    amount_paid = models.IntegerField(default=0)
    balance = models.IntegerField(default=0)
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE,
                                 related_name='employee_employeepaymenrecord', null=True)


@receiver(post_save, sender=Employees)
def create_employee_payment_record(sender, instance, created, **kwargs):
    if created:
        # Check if the associated user is not an admin
        if not instance.user.is_superuser:
            EmployeePaymentRecord.objects.create(employee=instance, id=instance.id)


class MonthlyTotal(models.Model):
    month = models.DateField(unique=True, null=True)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return f"Total Amount for {self.month}: {self.amount}"


@receiver(post_save, sender=Payment)
def update_monthly_total_amount(sender, instance, created, **kwargs):
        payment_month_first_day = instance.timestamp
        monthly_total_obj, created = MonthlyTotal.objects.get_or_create(month=payment_month_first_day)
        monthly_total_obj.amount += instance.amount_paid
        monthly_total_obj.save()


class TotalAmount(models.Model):
    date = models.DateField(unique=True, null=True)
    amount = models.IntegerField(default=0)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="client_total_amount", null=True)
    employee = models.ForeignKey(Employees, on_delete=models.SET_NULL, null=True, related_name="employess_total_amount")
    # def __str__(self):
    #     return f"Total Amount for {self.date}: {self.amount}"


@receiver(post_save, sender=Payment)
def update_total_amount(sender, instance, created, **kwargs):
        payment_date = instance.timestamp
        total_amount_obj, created = TotalAmount.objects.get_or_create(date=payment_date)
        total_amount_obj.amount += instance.amount_paid
        employee_superuser = Employees.objects.filter(user__is_superuser=True).first()
        total_amount_obj.employee = employee_superuser
        instance.approved_by = employee_superuser

        total_amount_obj.save()


