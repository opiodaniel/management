from django.urls import path
from .views import (
                    employee_dashboard, admin_dashboard,
                    employees_client, register, client_entry, add_client, login_page,
                    edit_user_profile_new, change_password, pay_employee, approve_employee_payment,
                    CustomLogoutView, edit_client, client_list, distributor_list, delete_employee, admin_add_client, get_client_details, free_clients,
                    download_free_clients, assign_client, claim_free_client, truncate_model, admin_access,
                    export_unapproved_payments, get_employee_with_clients_and_payments, activate_obj_function,
                    upload_file, get_data_link, attach_land_to_client, record_payment, add_land, land_list, update_land,
                    delete_land, edit_payment, clients_with_lands, land_transaction_history,
                    employee_clients_made_payment, edit_employee_payment, employee_pay_breakdown, client_payment)


app_name = 'realestates'

urlpatterns = [

    path('', login_page, name='login_page'),

    # ====== Admin =======
    path('administrator/<int:admin_id>/', admin_dashboard, name='admin_dashboard'),
    path('pay_employee/', pay_employee, name='pay_employee'),
    path('employee_clients/<int:employee_id>/', employee_clients_made_payment, name='employee_clients_made_payment'),
    path('edit_employee_payment/<int:employee_id>/<int:client_id>/<int:client_land_id>/<int:record_id>/', edit_employee_payment,
         name='edit_employee_payment'),
    path('approve_employee_payment/<int:employee_id>/<int:client_id>/<int:client_land_id>/', approve_employee_payment,
         name='approve_employee_payment'),

    path('attach_land/<int:client_id>/', attach_land_to_client, name='attach_land_to_client'),
    path('record_payment/<int:client_id>/', record_payment, name='record_payment'),
    path('edit-payment/<int:payment_id>/',   edit_payment, name='edit_payment'),

    path('client_list/', client_list, name='client_list'),
    path('distributor_list/', distributor_list, name='distributor_list'),
    path('employee/delete/<int:pk>/', delete_employee, name='delete_employee'),
    path('admin_add_client/', admin_add_client, name='admin_add_client'),
    path('get-client-details/', get_client_details, name='get_client_details'),
    path('client_payment/', client_payment, name='client_payment'),
    path('add_land/', add_land, name='add_land'),
    path('land_list/', land_list, name='land_list'),
    path('land/update/<int:land_id>/', update_land, name='update_land'),
    path('land/delete/<int:land_id>/', delete_land, name='delete_land'),

    path('clients_with_lands/', clients_with_lands, name='clients_with_lands'),
    path('land_transaction_history/<int:land_id>/', land_transaction_history, name='land_transaction_history'),

    path('free_clients/', free_clients, name='free_clients'),
    path('free-clients/assign/<int:client_id>/', assign_client, name='assign_client'),
    path('free-clients/download/', download_free_clients, name='download_free_clients'),
    path('admin_access/', admin_access, name='admin_access'),


    # ====== Employee =====
    path('employee/', employee_dashboard, name='employee_dashboard'),
    path('employees_client/', employees_client, name='employees_client'),
    path('client_entry/', client_entry, name='client_entry'),
    path('add_client/', add_client, name='add_client'),
    path('claim_free_client/', claim_free_client, name='claim_free_client'),
    path('edit_client/<pk>', edit_client, name='edit_client'),
    path('pay_breakdown/', employee_pay_breakdown, name='employee_pay_breakdown'),



    # Download Excel file
    path('export-unapproved-payments/', export_unapproved_payments, name='export_unapproved_payments'),
    path('employee-clients-payments/', get_employee_with_clients_and_payments, name='get_employee_with_clients_and_payments'),


    # ==========  User Registration ==========
    path(r'register/', register, name='register'),
    path('edit_user_profile_new', edit_user_profile_new, name='edit_user_profile_new'),
    path('change-password/', change_password, name='change_password'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    # ========== file upload and database clean up ===========
    path('upload_file/', upload_file, name='upload_file'),
    path('get_data_link', get_data_link, name='get_data_link'),
    path('activate_obj_function/', activate_obj_function, name='activate_obj_function'),
    path('truncate_model/', truncate_model, name='truncate_model'),

]
