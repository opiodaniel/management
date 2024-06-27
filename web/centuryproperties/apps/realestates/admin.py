from django.contrib import admin
from .models import (
    Company, Employees, Client, Land, ClientLand, Payment,
    Commission, EmployeePaymentRecord
)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'company_phone_number')
    search_fields = ('company_name', 'company_phone_number')


class EmployeesAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_administrator', 'phone', 'date_of_birth')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')
    list_filter = ('is_administrator',)


class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phoneNumber1', 'phoneNumber2', 'location', 'employee')
    search_fields = ('name', 'phoneNumber1', 'phoneNumber2', 'location')
    list_filter = ('employee',)


class LandAdmin(admin.ModelAdmin):
    list_display = ('plot_number', 'location', 'price')
    search_fields = ('plot_number', 'location')
    list_filter = ('location',)


class ClientLandAdmin(admin.ModelAdmin):
    list_display = ('client', 'land', 'purchase_date',  'total_amount_paid', 'remaining_amount', 'total_installments',)
    search_fields = ('client__name', 'land__plot_number')
    list_filter = ('purchase_date',)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('client_land', 'amount_paid',  'approved', 'approved_by', 'employee', 'timestamp') #'total_amount', 'remaining_amount', 'installment_number', 'total_installments',
    search_fields = ('employee__user__username', )
    list_filter = ('approved', 'timestamp')


class CommissionAdmin(admin.ModelAdmin):
    list_display = ('employee', 'client', 'total_commission', 'date_paid')
    search_fields = ('employee__user__username', 'client__name')
    list_filter = ('date_paid',)


class EmployeePaymentRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'total_commission', 'amount_paid', 'balance')
    search_fields = ('employee__user__username',)
    list_filter = ('employee',)


class MonthlyTotalAdmin(admin.ModelAdmin):
    list_display = ('month', 'amount')
    search_fields = ('month',)
    list_filter = ('month',)


class TotalAmountAdmin(admin.ModelAdmin):
    list_display = ('date', 'amount', 'client', 'employee')
    search_fields = ('date', 'client__name', 'employee__user__username')
    list_filter = ('date',)


admin.site.register(Company, CompanyAdmin)
admin.site.register(Employees, EmployeesAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Land, LandAdmin)
admin.site.register(ClientLand, ClientLandAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Commission, CommissionAdmin)
admin.site.register(EmployeePaymentRecord, EmployeePaymentRecordAdmin)
