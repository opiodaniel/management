from django.urls import path
from .views import (
                    employee_dashboard, admin_dashboard,
                    employees_client, register, approve_payment, confirm_payment, add_client, login_page,
                    edit_user_profile_new, change_password, pay_employee, approve_employee_payment, edit_employee_payment,
                    confirm_employee_payment, CustomLogoutView, edit_client, pending_payments_view,
                    client_list, free_clients, download_free_clients, assign_client, claim_free_client, truncate_model,
                    export_unapproved_payments, get_employee_with_clients_and_payments, activate_obj_function,
                    upload_file, get_data_link, record_payment, add_land, edit_payment, delete_payment,
                    clients_with_lands, land_transaction_history)


app_name = 'realestates'

urlpatterns = [

    path('', login_page, name='login_page'),

    path('administrator/<int:admin_id>/', admin_dashboard, name='admin_dashboard'),
    path('employee/', employee_dashboard, name='employee_dashboard'),
    path('employees_client/', employees_client, name='employees_client'),


    path('approve_payment/<int:client_id>/', approve_payment, name='approve_payment'),
    path('confirm_payment/<int:client_id>/', confirm_payment, name='confirm_payment'),

    path('pay_employee/', pay_employee, name='pay_employee'),
    path('approve_employee_payment/<int:employee_id>/', approve_employee_payment, name='approve_employee_payment'),
    path('edit_employee_payment/<int:payment_id>/', edit_employee_payment, name='edit_employee_payment'),

    path('confirm_employee_payment/<int:employee_id>/', confirm_employee_payment, name='confirm_employee_payment'),

    path('pending-payments/', pending_payments_view, name='pending_payments'),

    path('export-unapproved-payments/', export_unapproved_payments, name='export_unapproved_payments'),
    path('employee-clients-payments/', get_employee_with_clients_and_payments, name='get_employee_with_clients_and_payments'),



    path(r'register/', register, name='register'),

    path('client_list/', client_list, name='client_list'),
    path('record_payment/<int:client_id>/', record_payment, name='record_payment'),
    path('edit-payment/<int:payment_id>/',   edit_payment, name='edit_payment'),
    path('delete-payment/<int:payment_id>/', delete_payment, name='delete_payment'),
    path('add_land/', add_land, name='add_land'),
    path('clients_with_lands/', clients_with_lands, name='clients_with_lands'),
    path('land_transaction_history/<int:land_id>/', land_transaction_history, name='land_transaction_history'),

    path('add_client/', add_client, name='add_client'),
    path('edit_client/<pk>', edit_client, name='edit_client'),

    path('free_clients/', free_clients, name='free_clients'),
    path('free-clients/assign/<int:client_id>/', assign_client, name='assign_client'),
    path('claim_free_client/', claim_free_client, name='claim_free_client'),
    path('free-clients/download/', download_free_clients, name='download_free_clients'),

    path('edit_user_profile_new', edit_user_profile_new, name='edit_user_profile_new'),
    path('change-password/', change_password, name='change_password'),

    path('logout/', CustomLogoutView.as_view(), name='logout'),


    path('upload_file/', upload_file, name='upload_file'),
    path('get_data_link', get_data_link, name='get_data_link'),
    path('activate_obj_function/', activate_obj_function, name='activate_obj_function'),

    path('truncate_model/', truncate_model, name='truncate_model'),

]





