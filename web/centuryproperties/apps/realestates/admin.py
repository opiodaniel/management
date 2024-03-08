from django.contrib import admin
from .models import Employees, Client, Payment, MonthlyTotal,  TotalAmount, Company, EmployeePaymentRecord


class CompanyAdmin(admin.ModelAdmin):
    list_display = ['id', 'company_name', 'company_phone_number']


class EmployeesAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'is_administrator', 'created']
    list_filter = ['created', 'user']


class ClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'date', 'employee', 'phoneNumber1', 'phoneNumber2', 'location']
    list_filter = ('employee',)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'amount_paid',  'approved', 'timestamp', 'employee', 'approved_by')
    list_filter = ('approved', 'employee',)
    actions = ['approve_payments', 'reject_payments']


class EmployeePaymentRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'total_commission', 'amount_paid', 'balance', 'employee']


class MonthlyTotalAdmin(admin.ModelAdmin):
    list_display = ['id', 'month', 'amount', ]


class TotalAmountAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'amount', 'client', 'employee']


admin.site.register(Company, CompanyAdmin)
admin.site.register(Employees, EmployeesAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(EmployeePaymentRecord, EmployeePaymentRecordAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(MonthlyTotal, MonthlyTotalAdmin)
admin.site.register(TotalAmount, TotalAmountAdmin)