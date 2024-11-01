from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from datetime import timedelta, datetime, date
from django.core.validators import MinLengthValidator
from django.db.models import Sum
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, post_delete
from django.db import connection
from django.core.exceptions import ValidationError
from django.db import transaction

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
    exclude_from_reassignment = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    is_show = models.BooleanField(default=True)

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
            client_land__client__employee=self,
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
        # Count the distinct clients with approved payments
        return Payment.objects.filter(
            client_land__client__employee=self,
            approved=True
        ).values('client_land__client').distinct().count()

    def total_appending_clients(self):
        return Client.objects.filter(employee=self, client_lands__isnull=True).count()

    @classmethod
    def total_approved_clients_for_all_employee(cls):
        return sum(employee.total_approved_clients() for employee in cls.objects.all())

    @classmethod
    def total_appending_clients_for_all_employee(cls):
        return sum(employee.total_appending_clients() for employee in cls.objects.all())

    def __str__(self):
        return self.user.get_full_name()


@receiver(post_save, sender=User)
def create_employee(sender, instance, created, **kwargs):
    if created:
        Employees.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_employee(sender, instance, created, **kwargs):
    if created:
        instance.employee.save()


class Client(TruncateTableMixin, models.Model):
    name = models.CharField(max_length=100)
    phoneNumber1 = models.CharField(max_length=15, blank=True, default='', validators=[MinLengthValidator(7)])
    phoneNumber2 = models.CharField(max_length=15, blank=True, default='', null=True)
    location = models.CharField(max_length=30, default='', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, null=True)
    employee = models.ForeignKey(Employees, on_delete=models.SET_NULL, null=True, related_name="clients")
    expired_date = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['phoneNumber1'], name='unique_phoneNumber1'),
        ]

    def __str__(self):
        return self.name

    def is_editable(self):
        if self.date is None:
            return False
        return timezone.now() <= self.date + timedelta(hours=24)


class Land(TruncateTableMixin, models.Model):
    plot_number = models.CharField(max_length=255, blank=True, default='')
    location = models.CharField(max_length=255)
    price = models.IntegerField(default=0)
    available = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(price__gt=0), name='price_gt_0'),
        ]

    def __str__(self):
        return self.plot_number

    def clean(self):
        if self.price <= 0:
            raise ValidationError("Land price must be greater than zero.")

    def save(self, *args, **kwargs):
        self.clean()  # Ensure clean method is called before saving
        super().save(*args, **kwargs)


class ClientLand(TruncateTableMixin, models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_lands')
    land = models.ForeignKey(Land, on_delete=models.CASCADE, related_name='client_lands')
    purchase_date = models.DateField(null=True)
    total_installments = models.PositiveIntegerField(default=0)
    total_amount_paid = models.IntegerField(default=0)
    remaining_amount = models.IntegerField(default=0)
    payment_complete = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.client.name} - {self.land.plot_number}'

    def check_payment_status(self):
        if self.total_amount_paid > 0:
            self.land.available = False
            self.land.save()
        if self.total_amount_paid == self.land.price:
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

    def __str__(self):
        return f'{self.client_land.client.name} - {self.client_land.land.plot_number}'

    def save(self, *args, **kwargs):
        if self.pk:  # Check if this is an update
            old_instance = Payment.objects.get(pk=self.pk)
            # print('old_instance.amount_paid===', old_instance.amount_paid)
            # print('instance.amount_paid===', self.amount_paid)
            amount_diff = self.amount_paid - old_instance.amount_paid
            # print('amount_diff==', amount_diff)
        else:
            amount_diff = self.amount_paid
            # print('Nooo part amount_diff==', amount_diff)

        super().save(*args, **kwargs)

        client_land = self.client_land
        client_land.total_amount_paid += amount_diff  # === don't include plus sign when uploading excel file =====
        client_land.remaining_amount = client_land.land.price - client_land.total_amount_paid
        client_land.check_payment_status()
        client_land.purchase_date = self.timestamp
        client_land.save()

        # Update the client model's employee field to match the payment's employee
        client = client_land.client
        if self.employee and client.employee != self.employee:
            client.employee = self.employee
            client.save()

        # Update the employee field in existing commissions
        commissions = Commission.objects.filter(client=client, client_land=client_land)
        for commission in commissions:
            if commission.employee != self.employee:
                # Simply update the employee field of the existing commission
                commission.employee = self.employee
                commission.save()

    def delete(self, *args, **kwargs):
        client_land = self.client_land

        # Deduct the amount of this payment from the total amount paid
        client_land.total_amount_paid -= self.amount_paid
        client_land.remaining_amount = client_land.land.price - client_land.total_amount_paid

        # Check if there are remaining payments for this ClientLand
        remaining_payments = Payment.objects.filter(client_land=client_land).exclude(pk=self.pk).exists()

        if not remaining_payments:
            # If no remaining payments, reset the amounts
            client_land.total_amount_paid = 0
            client_land.remaining_amount = client_land.land.price
            client_land.payment_complete = False
            client_land.land.available = True  # Mark the land as available again
            client_land.land.save()

        # Save the updated client_land
        client_land.save()

        # Delete the payment record
        super().delete(*args, **kwargs)


class Commission(TruncateTableMixin, models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='commissions', null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='commissions', null=True)
    client_land = models.ForeignKey(ClientLand, on_delete=models.CASCADE, related_name='commission_payments', null=True)
    total_commission = models.IntegerField(default=0)
    date_paid = models.DateField(null=True)

    class Meta:
        unique_together = ('employee', 'client', 'client_land')

    def __str__(self):
        employee_name = self.employee.user.username if self.employee and self.employee.user else 'No employee'
        client_name = self.client.name if self.client else 'No client'
        land_plot_number = self.client_land.land.plot_number if self.client_land and self.client_land.land else 'No land'
        return f"Commission for {employee_name} from {client_name} (Land: {land_plot_number}): {self.total_commission}"


old_payment_amounts = {}


@receiver(pre_save, sender=Payment)
def capture_old_amount(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Payment.objects.get(pk=instance.pk)
        old_payment_amounts[instance.pk] = old_instance.amount_paid
    else:
        old_payment_amounts[instance.pk] = 0  # New instance, no old amount


@receiver(post_save, sender=Payment)
def update_commission(sender, instance, created, **kwargs):
    if instance.approved and instance.client_land.client.employee:
        commission, _ = Commission.objects.get_or_create(
            employee=instance.client_land.client.employee,
            client=instance.client_land.client,
            client_land=instance.client_land,
            defaults={'date_paid': instance.timestamp, 'total_commission': 0}
        )

        if created:
            # New payment creation
            new_commission = instance.amount_paid * 0.1
            commission.total_commission += new_commission
        else:
            # Update to existing payment
            old_amount_paid = old_payment_amounts.get(instance.pk, 0)
            amount_diff = instance.amount_paid - old_amount_paid

            # print('old_amount_paid===', old_amount_paid)
            # print('instance.amount_paid===', instance.amount_paid)
            # print('Update to existing payment===', amount_diff)

            # Calculate the commission adjustment based on the amount difference
            commission_adjustment = amount_diff * 0.1
            commission.total_commission += commission_adjustment

        # Update the commission's date paid to the latest payment's timestamp
        commission.date_paid = instance.timestamp
        commission.save()

        # Clean up the old_payment_amounts dictionary
        old_payment_amounts.pop(instance.pk, None)

# Signal to adjust commission on payment deletion
@receiver(post_delete, sender=Payment)
def adjust_commission_on_delete(sender, instance, **kwargs):
    if instance.approved and instance.client_land.client.employee:
        try:
            commission = Commission.objects.get(
                employee=instance.client_land.client.employee,
                client=instance.client_land.client,
                client_land=instance.client_land
            )

            # Check if there are any remaining payments for this ClientLand
            remaining_payments_exist = Payment.objects.filter(
                client_land=instance.client_land
            ).exists()

            if remaining_payments_exist:
                # If there are remaining payments, adjust the commission
                commission_reduction = instance.amount_paid * 0.1
                commission.total_commission -= commission_reduction
                commission.save()
            else:
                # If no remaining payments, delete the commission
                commission.delete()

        except Commission.DoesNotExist:
            # In case there is no commission record (shouldn't normally happen)
            pass


class EmployeePaymentRecord(TruncateTableMixin, models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='payment_records', null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='payment_records', null=True)
    client_land = models.ForeignKey(ClientLand, on_delete=models.CASCADE, related_name='payment_records', null=True)
    total_commission = models.IntegerField(default=0)
    amount_paid = models.IntegerField(default=0)
    balance = models.IntegerField(default=0)
    payment_date = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.employee.user.username} - Payment Record {self.id}"

    def save(self, *args, **kwargs):
        # Ensure balance is updated correctly
        self.balance = self.total_commission - self.amount_paid
        super().save(*args, **kwargs)

