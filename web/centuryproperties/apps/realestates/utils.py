# from datetime import date
# from .models import Payment, TotalAmount, MonthlyTotal
# from django.db.models import Sum
# from django.dispatch import receiver
# from django.db.models.signals import post_save
# from django.utils import timezone
#
# TOTAL_AMOUNT_KEY = 'total_amount'
#
#
# def total_amount_today():
#     # Get today's date
#     today = date.today()
#     print('==================  total_amount_today  =============================== ')
#     # Filter payments made today and aggregate the total amount
#     total_amount = Payment.objects.filter(timestamp__date=today).aggregate(total_amount=Sum('amount_paid'))['total_amount']
#
#     # If no payments made today, return 0
#     if total_amount is None:
#         total_amount = 0
#
#     return total_amount

#
# @receiver(post_save, sender=Payment)
# def update_total_amount(sender, instance, **kwargs):
#     # Get today's date
#     today = timezone.now().date()
#     print('==================  update_total_amount =============================== ')
#     # Get or create the total amount object for today
#     total_amount_obj, created = TotalAmount.objects.get_or_create(date=today)
#
#     # Update the total amount
#     total_amount_obj.amount = total_amount_today()
#     total_amount_obj.save()
#
#
# @receiver(post_save, sender=Payment)
# def update_monthly_total_amount(sender, instance, created, **kwargs):
#
#         # Get the first day of the payment month
#         payment_month_first_day = instance.timestamp
#         print('==================  update_monthly_total_amount =============================== ')
#         # Get or create the MonthlyTotal object for the payment month
#         monthly_total_obj, created = MonthlyTotal.objects.get_or_create(month=payment_month_first_day)
#
#         # Update the monthly total amount
#         monthly_total_obj.amount += instance.amount_paid
#         monthly_total_obj.save()