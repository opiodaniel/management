from django.urls import path
from .views import (
                    employee_dashboard, admin_dashboard,
                    employees_client, register, approve_payment, confirm_payment, add_client, login_page,
                    edit_user_profile_new, change_password, pay_employee, approve_employee_payment,
                    confirm_employee_payment, CustomLogoutView)


app_name = 'realestates'

urlpatterns = [

    path('', login_page, name='login_page'),

    path('administrator/<int:admin_id>/', admin_dashboard, name='admin_dashboard'),
    path('employee/<int:employee_id>/', employee_dashboard, name='employee_dashboard'),
    path('employees_client/', employees_client, name='employees_client'),

    path('approve_payment/<int:client_id>/', approve_payment, name='approve_payment'),
    path('confirm_payment/<int:client_id>/', confirm_payment, name='confirm_payment'),

    path('pay_employee/', pay_employee, name='pay_employee'),
    path('approve_employee_payment/<int:employee_id>/', approve_employee_payment, name='approve_employee_payment'),
    path('confirm_employee_payment/<int:employee_id>/', confirm_employee_payment, name='confirm_employee_payment'),


    path(r'register/', register, name='register'),
    path('add_client/', add_client, name='add_client'),

    path('edit_user_profile_new', edit_user_profile_new, name='edit_user_profile_new'),
    path('change-password/', change_password, name='change_password'),

    path('logout/', CustomLogoutView.as_view(), name='logout'),

]





