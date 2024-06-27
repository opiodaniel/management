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
from django.urls import reverse
from django.db.models import F
from django.utils import timezone


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
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        payments = Payment.objects.filter(
            employee=self,
            approved=True,
            timestamp__range=[start_of_week, end_of_week]
        ).order_by('timestamp')

        if payments.exists():
            for payment in payments:
                total_commission += payment.amount_paid * 0.1

        return total_commission

    # def calculate_weekly_commission(self):
    #     total_commission = 0
    #
    #     today = timezone.now().date()
    #     start_of_week = today - timedelta(days=today.weekday())  # Monday of the current week
    #     end_of_week = start_of_week + timedelta(days=6)  # Sunday of the current week
    #     print(start_of_week, end_of_week)
    #
    #     # Filter the payments made within the current week
    #     clients = Payment.objects.filter(
    #         client__employee=self,
    #         approved=True,
    #         # client__client_payment__remaining_amount=0,
    #         # timestamp__range=[start_of_week, end_of_week]
    #     ).order_by('timestamp')  # Sort by timestamp to ensure correct ordering
    #
    #     if clients.exists():
    #         # Calculate commission for each client
    #         for client in clients:
    #             total_commission += client.amount_paid * 0.1  # 10% commission for bringing a client
    #
    #     return total_commission

    def calculate_commission_from_client(self, client_id):
        try:
            commission = Commission.objects.get(employee=self, client_id=client_id)
            return commission.total_commission
        except Commission.DoesNotExist:
            return 0

    # ====pairing clients and 0.05 on the lower amount====
    # def calculate_weekly_commission(self):
    #     total_commission = 0
    #
    #     today = datetime.now().date()
    #     start_of_week = today - timedelta(days=today.weekday())  # Monday of the current week
    #     end_of_week = start_of_week + timedelta(days=6)  # Sunday of the current week
    #     print(start_of_week,  end_of_week)
    #     # Filter the payments made within the current week
    #     clients = Payment.objects.filter(
    #         client__employee=self,
    #         approved=True,
    #         timestamp__range=[start_of_week, end_of_week]
    #     ).order_by('timestamp')  # Sort by timestamp to ensure correct or
    #     print(clients)
    #
    #     if clients.exists():
    #         # Calculate commission for each client
    #         for client in clients:
    #             total_commission += client.amount_paid * 0.1  # 10% commission for bringing a client
    #             # print('alone', total_commission)
    #
    #         pair_count = len(clients) // 2
    #         remaining_clients = len(clients) % 2
    #         pair_commissions = []
    #         if pair_count > 0:
    #             amounts_paid = [client.amount_paid for client in clients]
    #             # print(amounts_paid)
    #             for i in range(pair_count):
    #                 pair_minimum_amount = min(amounts_paid[2 * i], amounts_paid[2 * i + 1])  #Take the minimum amount from each pair
    #                 total_commission += pair_minimum_amount * 0.05  # Additional 5% for every pair
    #                 pair_commissions.append(total_commission)
    #         total_commission += sum(pair_commissions)
    #         print('total_pair_commissions  ', total_commission)
    #
    #         if len(pair_commissions) > 0:
    #             total_commission = sum(pair_commissions)
    #
    #         If there's an odd number of clients, calculate commission for the last client individually
    #         if remaining_clients:
    #             if len(clients) % 2 == 1:  # Check if the last client is not part of a pair
    #                 total_commission += clients.last().amount_paid * 0.1  # 10% commission for the last client
    #
    #     return total_commission

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
    phoneNumber1 = models.CharField(max_length=15, blank=True, default='', validators=[MinLengthValidator(7)])
    phoneNumber2 = models.CharField(max_length=15, blank=True, default='', null=True)
    location = models.CharField(max_length=30, default='', blank=True, null=True)
    plot_number = models.CharField(max_length=20, blank=True, default='')
    date = models.DateTimeField(auto_now_add=True, null=True)  # DateTimeField to capture date and time
    employee = models.ForeignKey(Employees, on_delete=models.SET_NULL, null=True, related_name="client_employee")
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# class LandPurchase(models.Model):
#     client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="land_purchases")
#     plot_number = models.CharField(max_length=20, blank=True, default='')
#     purchase_date = models.DateField(auto_now_add=True)
#     employee = models.ForeignKey(Employees, on_delete=models.SET_NULL, null=True, related_name="employee_land_purchases")
#
#     def __str__(self):
#         return f"{self.client.name} - {self.plot_number}"
#
#
# class Payment(models.Model):
#     land_purchase = models.ForeignKey(LandPurchase, on_delete=models.CASCADE, related_name="payments")
#     amount_paid = models.IntegerField(default=0)
#     total_amount = models.IntegerField(default=0)
#     remaining_amount = models.IntegerField(default=0)
#     installment_number = models.PositiveIntegerField(default=1)
#     total_installments = models.PositiveIntegerField(default=1)
#     installment_date = models.DateField(auto_now_add=True, null=True)
#     approved = models.BooleanField(default=False)
#     approved_by = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='approved_payments', null=True)
#     employee = models.ForeignKey(Employees, on_delete=models.SET_NULL, related_name='employee_payments', null=True)
#     timestamp = models.DateField(auto_now_add=True, null=True)


class Payment(TruncateTableMixin, models.Model):
    # client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="client_payment")
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, related_name="client_payment", null=True)
    client_name = models.CharField(max_length=100, null=True, blank=True)
    amount_paid = models.IntegerField(default=0)
    total_amount = models.IntegerField(default=0)
    remaining_amount = models.IntegerField(default=0)
    installment_number = models.PositiveIntegerField(default=1)
    total_installments = models.PositiveIntegerField(default=1)
    installment_date = models.DateField(auto_now_add=True, null=True)
    plot_number = models.CharField(max_length=20, blank=True, default='')
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(Employees, on_delete=models.SET_NULL, related_name='approved_payments', null=True)
    employee = models.ForeignKey(Employees, on_delete=models.SET_NULL, related_name='employee_payments', null=True)
    timestamp = models.DateField(auto_now_add=True, null=True)


class Commission(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='commissions')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, related_name='commissions', null=True)
    client_name = models.CharField(max_length=100, null=True, blank=True)  # New field to store client name
    total_commission = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('employee', 'client')

    def __str__(self):
        return f"Commission for {self.employee.user.username} from {self.client_name if self.client_name else 'Unknown Client'}: {self.total_commission}"


# @receiver(post_save, sender=Payment)
# def update_commission(sender, instance, **kwargs):
#     if instance.approved:
#         # Get or create the commission record for the employee and client
#         commission, created = Commission.objects.get_or_create(
#             employee=instance.client.employee,
#             client=instance.client
#         )
#
#         # Calculate the new commission based on the payment amount
#         new_commission = instance.amount_paid * 0.1  # Assuming 10% commission
#         commission.total_commission = new_commission
#
#         # Save the updated commission
#         commission.save()

@receiver(post_save, sender=Payment)
def update_commission(sender, instance, **kwargs):
    if instance.approved:
        # Get or create the commission record for the employee and client
        commission, created = Commission.objects.get_or_create(
            employee=instance.employee,  # Use instance.employee instead of instance.client.employee
            client=instance.client
        )

        # Calculate the new commission based on the payment amount
        new_commission = instance.amount_paid * 0.1  # Assuming 10% commission
        commission.total_commission = new_commission
        commission.client_name = instance.client.name  # Set client_name

        # Save the updated commission
        commission.save()


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



# @receiver(post_save, sender=Payment)
# def update_total_amount(sender, instance, created, **kwargs):
#     if created:
#         payment_date = instance.timestamp
#         total_amount_obj, _ = TotalAmount.objects.get_or_create(date=payment_date)
#         total_amount_obj.amount += instance.amount_paid
#         employee_superuser = Employees.objects.filter(user__is_superuser=True).first()
#         total_amount_obj.employee = employee_superuser
#         instance.approved_by = employee_superuser
#         total_amount_obj.save()



# from django.db import models
# from django.contrib.auth.models import User
# import datetime
# import decimal
# from .sql import TruncateTableMixin
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from ckeditor_uploader.fields import RichTextUploadingField
# from datetime import date
# from phonenumber_field.modelfields import PhoneNumberField
# from datetime import datetime, timedelta
# from django.core.validators import MinLengthValidator
# from django.urls import reverse
# from django.db.models import F
# from django.utils import timezone
#
#
# class Company(TruncateTableMixin, models.Model):
#     company_name = models.CharField(max_length=50, default='', blank=True)
#     company_logo = models.ImageField(upload_to='company_logo/', blank=True, null=True,
#                                      default='company_logo/default_company_logo/default_company_logo.jpeg')
#     company_phone_number = models.CharField('phone', max_length=20, default='', blank=True)
#
#
# class Employees(TruncateTableMixin, models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
#     is_administrator = models.BooleanField(default=False)
#
#     created = models.DateTimeField(auto_now_add=True, null=True)
#     updated = models.DateTimeField(auto_now=True)
#     is_confirmed = models.BooleanField(default=True)
#
#     short_bio = RichTextUploadingField('short_bio', blank=True, null=True)
#     bio = RichTextUploadingField('bio', blank=True, null=True)
#     #
#     address = models.CharField('address', max_length=128, default='', blank=True)
#     zip = models.CharField('zip', max_length=20, default='', blank=True)
#     city = models.CharField('city', max_length=100, default='', blank=True)
#     country = models.CharField('country', max_length=100, default='', blank=True)
#     #
#     phone = models.CharField('phone', max_length=20, default='', blank=True)
#     # date format, 1998-12-28
#     date_of_birth = models.DateField(blank=True, null=True)
#
#     profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True,
#                                     default='profile_pics/default_profile_pic/default.jpg')
#
#     def calculate_weekly_commission(self):
#         total_commission = 0
#
#         today = timezone.now().date()
#         start_of_week = today - timedelta(days=today.weekday())
#         end_of_week = start_of_week + timedelta(days=6)
#
#         payments = Payment.objects.filter(
#             employee=self,
#             approved=True,
#             timestamp__range=[start_of_week, end_of_week]
#         ).order_by('timestamp')
#
#         if payments.exists():
#             for payment in payments:
#                 total_commission += payment.amount_paid * 0.1
#
#         return total_commission
#
#     def calculate_commission_from_client(self, client_id):
#         try:
#             commission = Commission.objects.get(employee=self, client_id=client_id)
#             return commission.total_commission
#         except Commission.DoesNotExist:
#             return 0
#
#     def total_clients(self):
#         return self.client_employee.count()
#
#     def total_approved_clients(self):
#         return Payment.objects.filter(client__employee=self, approved=True).count()
#
#     def total_appending_clients(self):
#         return Payment.objects.filter(client__employee=self, approved=False).count()
#
#     @classmethod
#     def total_approved_clients_for_all_employee(cls):
#         return sum(employee.client_employee.filter(approved=True).count() for employee in cls.objects.all())
#
#     @classmethod
#     def total_appending_clients_for_all_employee(cls):
#         return sum(employee.client_employee.filter(approved=False).count() for employee in cls.objects.all())
#
#     def __str__(self):
#         return self.user.get_full_name()
#
#
# @receiver(post_save, sender=User)
# def create_employee(sender, instance, created, **kwargs):
#     if created:
#         Employees.objects.create(user=instance, id=instance.id)
#
#
# @receiver(post_save, sender=User)
# def save_employee(sender, instance, created, **kwargs):
#     if created:
#         instance.employee.save()
#
#
# class Client(TruncateTableMixin, models.Model):
#     name = models.CharField(max_length=100)
#     phoneNumber1 = models.CharField(max_length=15, blank=True, default='', validators=[MinLengthValidator(7)])
#     phoneNumber2 = models.CharField(max_length=15, blank=True, default='', null=True)
#     location = models.CharField(max_length=30, default='', blank=True, null=True)
#     plot_number = models.CharField(max_length=20, blank=True, default='')
#     date = models.DateTimeField(auto_now_add=True, null=True)  # DateTimeField to capture date and time
#     employee = models.ForeignKey(Employees, on_delete=models.SET_NULL, null=True, related_name="client_employee")
#     completed = models.BooleanField(default=False)
#
#     def __str__(self):
#         return self.name
#
#     def check_and_delete_if_completed(self):
#         payments = self.client_payment.all()
#         print(f"Checking client {self.name} for deletion. Payments count: {payments.count()}")
#         if all(payment.approved and payment.remaining_amount == 0 for payment in payments):
#             print(f"Deleting client {self.name}")
#             self.completed = True
#             self.save()
#             self.delete()
#
# class Payment(TruncateTableMixin, models.Model):
#     # client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="client_payment")
#     client = models.ForeignKey(Client, on_delete=models.SET_NULL, related_name="client_payment", null=True)
#     client_name = models.CharField(max_length=100, null=True, blank=True)
#     amount_paid = models.IntegerField(default=0)
#     total_amount = models.IntegerField(default=0)
#     remaining_amount = models.IntegerField(default=0)
#     installment_number = models.PositiveIntegerField(default=1)
#     total_installments = models.PositiveIntegerField(default=1)
#     installment_date = models.DateField(auto_now_add=True, null=True)
#     plot_number = models.CharField(max_length=20, blank=True, default='')
#     approved = models.BooleanField(default=False)
#     approved_by = models.ForeignKey(Employees, on_delete=models.SET_NULL, related_name='approved_payments', null=True)
#     employee = models.ForeignKey(Employees, on_delete=models.SET_NULL, related_name='employee_payments', null=True)
#     timestamp = models.DateField(auto_now_add=True, null=True)
#
#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         if self.approved and self.remaining_amount == 0 and self.client:
#             print(f"Calling check_and_delete_if_completed for client {self.client.name}")
#             self.client.check_and_delete_if_completed()
#
#
# class Commission(models.Model):
#     employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='commissions')
#     client = models.ForeignKey(Client, on_delete=models.SET_NULL, related_name='commissions', null=True)
#     client_name = models.CharField(max_length=100, null=True, blank=True)  # New field to store client name
#     total_commission = models.IntegerField(default=0)
#     last_updated = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         unique_together = ('employee', 'client')
#
#     def __str__(self):
#         return f"Commission for {self.employee.user.username} from {self.client_name if self.client_name else 'Unknown Client'}: {self.total_commission}"
#
#
#
#
# @receiver(post_save, sender=Payment)
# def update_commission(sender, instance, **kwargs):
#     if instance.approved:
#         # Get or create the commission record for the employee and client
#         commission, created = Commission.objects.get_or_create(
#             employee=instance.employee,  # Use instance.employee instead of instance.client.employee
#             client=instance.client
#         )
#
#         # Calculate the new commission based on the payment amount
#         new_commission = instance.amount_paid * 0.1  # Assuming 10% commission
#         commission.total_commission = new_commission
#         commission.client_name = instance.client.name  # Set client_name
#
#         # Save the updated commission
#         commission.save()
#
#
# class EmployeePaymentRecord(TruncateTableMixin, models.Model):
#     total_commission = models.IntegerField(default=0)
#     amount_paid = models.IntegerField(default=0)
#     balance = models.IntegerField(default=0)
#     employee = models.ForeignKey(Employees, on_delete=models.CASCADE,
#                                  related_name='employee_employeepaymenrecord', null=True)
#
#
# @receiver(post_save, sender=Employees)
# def create_employee_payment_record(sender, instance, created, **kwargs):
#     if created:
#         # Check if the associated user is not an admin
#         if not instance.user.is_superuser:
#             EmployeePaymentRecord.objects.create(employee=instance, id=instance.id)
#
#
# class MonthlyTotal(models.Model):
#     month = models.DateField(unique=True, null=True)
#     amount = models.IntegerField(default=0)
#
#     def __str__(self):
#         return f"Total Amount for {self.month}: {self.amount}"
#
#
# @receiver(post_save, sender=Payment)
# def update_monthly_total_amount(sender, instance, created, **kwargs):
#         payment_month_first_day = instance.timestamp
#         monthly_total_obj, created = MonthlyTotal.objects.get_or_create(month=payment_month_first_day)
#         monthly_total_obj.amount += instance.amount_paid
#         monthly_total_obj.save()
#
#
# class TotalAmount(models.Model):
#     date = models.DateField(unique=True, null=True)
#     amount = models.IntegerField(default=0)
#     client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="client_total_amount", null=True)
#     employee = models.ForeignKey(Employees, on_delete=models.SET_NULL, null=True, related_name="employess_total_amount")
#     # def __str__(self):
#     #     return f"Total Amount for {self.date}: {self.amount}"
#
#
# @receiver(post_save, sender=Payment)
# def update_total_amount(sender, instance, created, **kwargs):
#         payment_date = instance.timestamp
#         total_amount_obj, created = TotalAmount.objects.get_or_create(date=payment_date)
#         total_amount_obj.amount += instance.amount_paid
#         employee_superuser = Employees.objects.filter(user__is_superuser=True).first()
#         total_amount_obj.employee = employee_superuser
#         instance.approved_by = employee_superuser
#
#         total_amount_obj.save()
#
#
#
