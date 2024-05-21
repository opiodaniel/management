from django.shortcuts import render, redirect,  get_object_or_404

from django.contrib import messages
from django.contrib.auth.models import User,auth

from .models import Client, Employees, Payment, MonthlyTotal, TotalAmount, Company
from .forms import ClientForm, ClientEditForm, EmployeeLoginForm, RegistrationForm, ProfileEditForm, UserEditForm

from django.contrib.auth import authenticate, login

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from django.core.mail import send_mail

from datetime import date
from django.utils import timezone

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .utils import total_amount_today
from .tasks import remove_inactive_clients


from django.views.generic.edit import FormView

from django.urls import reverse, reverse_lazy

from django.db.models import Sum
from .forms import MessageForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
import json
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from django.http import HttpResponse
from .models import EmployeePaymentRecord
from django.db import transaction
from django.contrib.auth import logout
from django.views.generic import View
from django import forms

from django.apps import apps
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q
import logging

def login_page(request):
    company = Company.objects.get(id=1)
    company_logo_url = company.company_logo.url
    arg = {
           'company_logo_url': company_logo_url
           }
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        # user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:  # Check if user is admin
                # return redirect('admin_dashboard')  # Redirect admin to admin dashboard
                # print(user)
                # print(user.id)
                # messages.info(request, f"You are now logged in as {username}.")
                return redirect(reverse('realestates:admin_dashboard', args=[user.id]))
            else:
                # messages.info(request, f"You are now logged in as {username}.")
                return redirect(reverse('realestates:employee_dashboard', args=[user.id]))
        else:
            messages.error(request, "Invalid username or password.")

        # if user is not None:
        #     # Login user
        #     login(request, user)
        #     messages.success(request, 'You have successfully logged in.')
        #     return redirect('home')  # Redirect to home page after successful login
        # else:
        #     messages.error(request, 'Invalid username or password.')
        #     return redirect('login')  # Redirect back to login page with error message

    # If request method is GET, render the login page
    return render(request, 'realestates/registration/login.html', arg)

@login_required
# def home(request):
#     return render(request, "home.html")
def get_total_sales_for_month(request, year, month):
    # Define the start date of the month
    start_date = datetime(year, month, 1)
    # Define the end date of the month
    end_date = datetime(year, month, 1) + timedelta(days=32)
    end_date = datetime(end_date.year, end_date.month, 1) - timedelta(days=1)
    # Calculate the total sales for the month
    total_sales = Payment.objects.filter(timestamp__range=[start_date, end_date]).aggregate(total_sales=Sum('amount_paid'))['total_sales']
    # print(total_sales)
    # If no sales, return 0
    if total_sales is None:
        total_sales = 0
    return total_sales


def get_total_sales_for_previous_months(request):
    total_sales_previous_months = []
    total_sales_previous_months_sum = 0
    # Get the current year and month
    current_year = datetime.now().year
    current_month = datetime.now().month
    # Iterate over previous months
    for month in range(1, current_month):
        total_sales = get_total_sales_for_month(request, current_year, month)
        total_sales_previous_months.append((datetime(current_year, month, 1), total_sales))
        total_sales_previous_months_sum += total_sales
    # Calculate total sales for the current month
    total_sales_current_month = get_total_sales_for_month(request, current_year, current_month)
    # print('=== total_sales_current_month === ', total_sales_current_month)
    total_sales_previous_months.append((datetime(current_year, current_month, 1), total_sales_current_month))
    total_sales_previous_months_sum += total_sales_current_month
    # print('=== total_sales_previous_months_sum === ', total_sales_previous_months_sum)
    return total_sales_previous_months, total_sales_previous_months_sum


@login_required
def admin_dashboard(request, admin_id):

    DEfault_thresholdInput1 = 2
    DEfault_thresholdInput = 100

    if request.method == 'POST' and 'confirm_client_payment' in request.POST:
        # Reset the entry date of expired clients to the current date
        client_id = request.POST.get('client_id')
        # client = employee.client_employee.get(id=client_id)
        client = Client.objects.get(id=client_id)
        print(client)
        return redirect(reverse('realestates:employee_dashboard', args=[request.user.id]))

    authenticated_admin = request.user.id

    if authenticated_admin != int(admin_id):
        return redirect(reverse('realestates:admin_dashboard', args=[request.user.id]))

    company = Company.objects.get(id=1)
    company_logo_url = company.company_logo.url

    # total_amount = total_amount_today()
    # print(total_amount)

    # cut_of_date = remove_inactive_clients()
    # print(cut_of_date)

    # Get the current month
    current_month = datetime.now().month
    # print(current_month)
    # Define the start date of the month
    start_date = datetime(datetime.now().year, current_month, 1)
    # print(start_date)
    # Define the end date of the month
    end_date = datetime(datetime.now().year, current_month + 1, 1) - timedelta(days=1)
    # print(end_date)

    # Calculate the total amount made in the month
    total_amount_month = Payment.objects.filter(timestamp__range=[start_date, end_date]).aggregate(
        total_amount_month=Sum('amount_paid'))['total_amount_month']

    if total_amount_month is None:
        total_amount_month = 0
    total_amount_month_ = total_amount_month
    total_amount_month = '{:,}'.format(total_amount_month_)
    # print(total_amount_month)

    total_sales_previous_months, total_sales_previous_months_sum = get_total_sales_for_previous_months(request)

    monthly_data = []
    month_name_to_number = {
        "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
        "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
    }
    for month, total_sales in total_sales_previous_months:
        # print(f"Total sales for {month.strftime('%B %Y')}: {total_sales}")
        month_number = month_name_to_number[month.strftime('%B')]
        selected_year = month.strftime('%Y')
        amount_details_in_month = Payment.objects.filter(timestamp__month=month_number, timestamp__year=selected_year).filter(approved=True)
        monthly_data.append({
            'date': month.strftime('%B %Y'),
            'amount': "{:,}".format(total_sales),
            'month_detail': amount_details_in_month,
        })
    total_sales_previous_months_sum_ = total_sales_previous_months_sum
    total_sales_previous_months_sum = '{:,}'.format(total_sales_previous_months_sum_)
    # print(monthly_data)

    # Print the sum of all sales for the previous months
    # print(f"Sum of total sales for previous months: {total_sales_previous_months_sum}")
    # print(monthly_data)

    # Get today's date
    today = date.today()

    # Filter payments made today and aggregate the total amount

    total_amount_made_today = Payment.objects.filter(timestamp=today).aggregate(total_amount_made_today=Sum('amount_paid'))['total_amount_made_today']

    # # If no payments made today, return 0
    if total_amount_made_today is None:
        total_amount_made_today = 0

    # Filter payments made before today and aggregate the total amount
    total_amount_previous_days = Payment.objects.filter(timestamp__lt=today).aggregate(total_amount_previous_days=Sum('amount_paid'))['total_amount_previous_days']

    # If no payments made in previous days, return 0
    if total_amount_previous_days is None:
        total_amount_previous_days = 0
    total_sale_for_today_previous_days = total_amount_made_today + total_amount_previous_days
    admin = Employees.objects.get(id=admin_id)
    employees = Employees.objects.filter(is_administrator=False)

    payments = Payment.objects.filter(approved=False).order_by('approved', '-client__date')
    profile_pic_url = admin.profile_pic.url
    total_num_clients_ = Client.objects.all().count()
    total_number_employees = Employees.objects.filter(is_administrator=False).count()

    context = {
        'employee': admin,
        'admin_id': admin_id,
        'profile_pic_url': profile_pic_url,
        'employees': employees,
        'payments': payments,
        'total_number_employees': total_number_employees,
        'total_num_clients_': total_num_clients_,
        'total_amount_made_today': total_amount_made_today,
        'total_sale_for_today_previous_days': total_sale_for_today_previous_days,
        'company': company,
        'company_logo_url': company_logo_url,
        'total_amount_month': total_amount_month,
        'total_sales_previous_months_sum': total_sales_previous_months_sum,
        'monthly_data': monthly_data,
        "DEfault_thresholdInput1": DEfault_thresholdInput1,
        "DEfault_thresholdInput":  DEfault_thresholdInput,
    }
    return render(request, 'realestates/admin_dashboard.html', context)


@login_required
def employee_dashboard(request, employee_id):

    # Retrieve the authenticated employee
    authenticated_employee = request.user.id

    # Ensure that the authenticated employee matches the requested employee_id
    if authenticated_employee != int(employee_id):
        # Return a response indicating unauthorized access
        # return render(request, 'registration/unauthorized.html')  # You can customize this template as needed
        return redirect(reverse('realestates:employee_dashboard', args=[request.user.id]))

    company = Company.objects.get(id=1)
    company_logo_url = company.company_logo.url

    # Retrieve the employee object based on the employee_id
    employee = get_object_or_404(Employees, id=employee_id)
    payments = Payment.objects.filter(employee=employee).order_by('approved', '-client__date')
    profile_pic_url = employee.profile_pic.url

    employee_payment_record = EmployeePaymentRecord.objects.get(employee=employee)

    # weekly_commission = employee_payment_record.total_commission
    # print(weekly_commission)
    #
    # total_weekly_commission_ = int(weekly_commission)
    #
    # total_weekly_commission = '{:,}'.format(total_weekly_commission_)

    total_number_of_clients = employee.total_clients()
    total_approved_clients = employee.total_approved_clients()
    total_appending_clients = employee.total_appending_clients()

    expiry_date = timezone.now().date() - timedelta(days=7)
    clients = employee.client_employee.all()
    expired_clients = employee.client_employee.filter(date__lt=expiry_date)  # client_payment__approved=False

    approved_clients_count = Payment.objects.filter(employee_id=employee_id, approved=True).count()
    pending_clients_count = Payment.objects.filter(employee_id=employee_id, approved=False).count()

    if request.method == 'POST' and 'reset_expired_clients' in request.POST:
        # Reset the entry date of expired clients to the current date
        client_id = request.POST.get('client_id')
        # client = employee.client_employee.get(id=client_id)
        client = Client.objects.get(id=client_id)
        expiry_date = timezone.now().date() - timedelta(days=7)
        if client.date < expiry_date:
            # Update the client's date to the current date
            client.date = timezone.now()
            # Set the employee field to the current employee
            client.employee = request.user.employee  # Assuming the logged-in user is an employee
            # Save the changes to the database
            client.save()
        return redirect(reverse('realestates:employee_dashboard', args=[request.user.id]))

    context = {
        'employee': employee,
        'profile_pic_url': profile_pic_url,
        # 'total_weekly_commission': total_weekly_commission,
        'clients': clients,
        'expiry_date': expiry_date,
        'expired_clients': expired_clients,
        'total_number_of_clients': total_number_of_clients,
        'total_approved_clients': total_approved_clients,
        'total_appending_clients': total_appending_clients,
        'payments': payments,
        'company_logo_url': company_logo_url,
        'employee_payment_record': employee_payment_record,
    }

    # Render the employee dashboard template
    return render(request, 'realestates/employee_dashboard.html', context)


@login_required
def employees_client(request):
    employees = Employees.objects.filter(is_administrator=False)

    # Annotate employees with the count of approved and appending clients
    employees = employees.annotate(
        approved_clients=Count('employee_payments', filter=Q(employee_payments__approved=True)),
        appending_clients=Count('employee_payments', filter=Q(employee_payments__approved=False))
    ).prefetch_related('employee_payments__client')

    dic_ = {}

    for employee in employees:
        employee_clients = [
            {
                'id': payment.client.id,
                'name': payment.client.name,
                # Add other client fields as needed
            }
            for payment in employee.employee_payments.all()
        ]

        dic_[employee.user.username] = {
            'approved_clients': employee.approved_clients,
            'appending_clients': employee.appending_clients,
            'clients': employee_clients
        }

    return JsonResponse(dic_)
# def employees_client(request):
#     employees = Employees.objects.filter(is_administrator=False)
#     dic_ = {}
#
#     for employee in employees:
#         approved_clients = Payment.objects.filter(employee=employee, approved=True).count()
#         appending_clients = Payment.objects.filter(employee=employee, approved=False).count()
#
#         employee_clients = []
#         for payment in Payment.objects.filter(employee=employee):
#             client_dict = {
#                 'id': payment.client.id,
#                 'name': payment.client.name,
#                 # Add other client fields as needed
#             }
#             employee_clients.append(client_dict)
#
#         dic_[employee.user.username] = {
#             'approved_clients': approved_clients,
#             'appending_clients': appending_clients,
#             'clients': employee_clients
#         }
#     return JsonResponse(dic_)


@login_required
def expired_clients_list(request):
    company = Company.objects.get(id=1)
    company_logo_url = company.company_logo.url
    employee_id = request.user.id
    # Retrieve the employee object based on the employee_id
    employee = get_object_or_404(Employees, id=employee_id)

    profile_pic_url = employee.profile_pic.url
    expiry_date = timezone.now().date() - timedelta(days=7)
    print(expiry_date)

    # Retrieve expired clients
    # all_expired_clients = Client.objects.filter(date__lt=expiry_date, client_payment__approved=False)

    # Retrieve expired clients for a specific employee
    expired_clients = employee.client_employee.filter(date__date__lt=expiry_date, client_payment__approved=False)
    print(expired_clients)
    if request.method == 'POST' and 'reset_expired_clients' in request.POST:
        # Reset the entry date of expired clients to the current date
        client_id = request.POST.get('client_id')
        print(client_id)
        # client = employee.client_employee.get(id=client_id)
        client = Client.objects.get(id=client_id)
        payment = Payment.objects.get(client=client)
        print(payment)
        expiry_date = timezone.now().date() - timedelta(days=7)
        if client.date.date() < expiry_date:
            # Update the client's date to the current date
            client.date = timezone.now()
            # Set the employee field to the current employee
            client.employee = request.user.employee  # Assuming the logged-in user is an employee
            # Update the existing payment record with the new employee
            payment.employee = request.user.employee   # Assign the new employee to the payment
            # Save the changes to the database
            client.save()
            payment.save()

    context = {
        'expired_clients': expired_clients,
        'company_logo_url': company_logo_url,
        'profile_pic_url': profile_pic_url,
        'employee_id': employee_id
    }
    return render(request, 'realestates/expired_clients.html', context)


@login_required
def approve_payment(request, client_id):
    print(client_id)
    payment_client_id = client_id
    employee_id = request.POST.get('employee_id')
    # print('employee_id============', employee_id)
    client = Client.objects.get(id=client_id)
    context = {
        'payment_client_id': payment_client_id,
        'client': client,
        'employee_id': employee_id,
    }
    return render(request, 'realestates/confirm_client_payment.html', context)


@transaction.atomic
def confirm_payment(request, client_id):
    if request.method == 'POST':
        client = Client.objects.get(id=client_id)
        amount_paid_str = request.POST.get('amount_paid', '0').replace(',', '')  # Remove commas
        total_amount_str = request.POST.get('total_amount', '0').replace(',', '')  # Remove commas
        plot_number = request.POST.get('plot_number', '')
        amount_paid = int(amount_paid_str)
        total_amount = int(total_amount_str)
        if amount_paid <= 0 or total_amount <= 0:
            message = 'You must enter a valid positive amount.'
            return render(request, 'realestates/confirm_client_payment.html',
                          {'payment_client_id': client_id, 'message': message, 'client': client})

        if amount_paid > total_amount:
            message = 'Amount paid cannot be greater than the Expected amount.'
            return render(request, 'realestates/confirm_client_payment.html',
                          {'payment_client_id': client_id, 'message': message, 'client': client})

        else:
            # Assuming the request.user is the user making the request
            current_user = request.user

            # Check if the current user is a superuser (admin)
            if current_user.is_staff:
                # Get the associated employee record for the admin user
                # print(current_user, 'I am a superuser')
                try:
                    admin_employee = Employees.objects.get(user=current_user)
                except Employees.DoesNotExist as ex:
                    # print('=======ex=============', ex)
                    # Handle the case where the admin's employee record doesn't exist
                    # This might occur if the admin's employee record is not properly set up
                    # Log an error or handle the situation appropriately
                    return HttpResponse("Error: Admin employee record not found.")
                # employee = get_object_or_404(Employees, id=employee_id)
                # commission_earned = employee.calculate_commission()

                # Now you have the admin employee instance available (admin_employee)
                # Perform actions based on the admin's status

                # Assuming you have the client object
                client = Client.objects.get(pk=client_id)

                # Update the approved field of the client's payment
                payment = Payment.objects.get(client=client)
                payment.amount_paid += amount_paid
                # Check if total_amount has been set
                if payment.total_amount == 0:
                    payment.total_amount = total_amount  # Set the initial total_amount

                payment.remaining_amount = payment.total_amount - payment.amount_paid  # Update remaining amount
                payment.timestamp = date.today()
                payment.approved = True
                payment.approved_by = admin_employee
                payment.plot_number = plot_number
                payment.save()
                client.plot_number = plot_number
                client.save()
                # payment = Payment.objects.get(client=client)
                # payment.amount_paid += amount_paid  # Increment the amount_paid
                # payment.remaining_amount = payment.total_amount - payment.amount_paid  # Recalculate remaining_amount
                # if payment.remaining_amount == 0:
                #     payment.approved = True  # Mark as approved if fully paid
                # payment.timestamp = date.today()
                # payment.approved_by = admin_employee
                # payment.save()

                # TO USE THIS CODE SOON. IT'S A NEW UPDATE. ONLY CALCULATES FOR A PARTICULAR EMPLOYEE.
                # employee_id = request.POST.get('employee_id')
                # print('employee_id=1222222222222222', employee_id)
                # employee__ = Employees.objects.get(id=employee_id)
                # print('employee_id-----employee ', employee_id,  employee__)
                # weekly_commission = employee__.calculate_weekly_commission()
                # employee_payment_record, created = EmployeePaymentRecord.objects.get_or_create(
                #     employee=employee__)
                # employee_payment_record.total_commission += weekly_commission
                # employee_payment_record.balance = employee_payment_record.total_commission - employee_payment_record.amount_paid
                # employee_payment_record.save()
                # END OF THE CODE

                logging.basicConfig(level=logging.INFO)
                # Update EmployeePaymentRecord
                for employee in Employees.objects.filter(is_administrator=False):
                    try:
                        weekly_commission = employee.calculate_weekly_commission()
                        all_employee_payment_record, created = EmployeePaymentRecord.objects.get_or_create(
                            employee=employee)

                        logging.info(f'Employee: {employee.id}, Calculated Weekly Commission: {weekly_commission}')

                        # Update total commission by adding the weekly commission
                        all_employee_payment_record.total_commission += weekly_commission
                        all_employee_payment_record.balance = all_employee_payment_record.total_commission - all_employee_payment_record.amount_paid
                        all_employee_payment_record.save()

                        logging.info(
                            f'Updated Employee: {employee.id}, Total Commission: {all_employee_payment_record.total_commission}, Weekly Commission: {weekly_commission}, Balance: {all_employee_payment_record.balance}')

                    except EmployeePaymentRecord.DoesNotExist:
                        logging.error(
                            f'Payment record for employee {employee.id} does not exist and could not be created.')
                    except Exception as e:
                        logging.error(f'An error occurred while updating employee {employee.id}: {e}')

                # # Calculate commission for non-admin employees
                # for employee in Employees.objects.filter(is_administrator=False):  # Exclude superuser (admin)
                #     commission_earned = employee.calculate_weekly_commission()  # Implement this function according to your logic
                #
                #     # Update EmployeePaymentRecord for the employee
                #     employee_payment_record, _ = EmployeePaymentRecord.objects.get_or_create(employee=employee)
                #     employee_payment_record.total_commission = commission_earned
                #     employee_payment_record.save()

                return redirect(reverse('realestates:admin_dashboard', args=[request.user.id]))
            else:
                return HttpResponse("Error: You are not authorized to approve payments.")
    return render(request, 'realestates/confirm_client_payment.html')


@login_required
def pay_employee(request):
    admin_id = request.user.id
    admin = Employees.objects.get(id=request.user.id)
    profile_pic_url = admin.profile_pic.url
    company = Company.objects.get(id=1)
    company_logo_url = company.company_logo.url
    employees = Employees.objects.all().filter(is_administrator=False)
    all_employee_payment_record = EmployeePaymentRecord.objects.filter(employee__in=employees)
    context = {
        'employees': employees,
        'admin_id': admin_id,
        'company_logo_url': company_logo_url,
        'profile_pic_url': profile_pic_url,
        'all_employee_payment_record': all_employee_payment_record,
    }

    return render(request, 'realestates/pay_employee.html', context)


@login_required
def approve_employee_payment(request, employee_id):
    employee_id_ = employee_id
    employee = Employees.objects.get(id=employee_id)
    employee_payment_record = EmployeePaymentRecord.objects.get(employee=employee)
    print(employee_payment_record.total_commission)
    context = {
        'employee_id': employee_id_,
        'employee': employee,
        'employee_payment_record': employee_payment_record,
    }
    return render(request, 'realestates/confirm_employee_payment.html', context)


@login_required
def confirm_employee_payment(request, employee_id):
    if request.method == 'POST':
        # Get the amount paid from the form data
        amount_paid_str = request.POST.get('amount_paid', '0').replace(',', '')  # Remove commas
        amount_paid = int(amount_paid_str)
        if amount_paid <= 0:
            message = 'Amount must be greater than zero.'
            return render(request, 'realestates/confirm_employee_payment.html',
                          {'employee_id': employee_id, 'message': message})

        employee = Employees.objects.get(id=employee_id)
        all_employee_payment_record = EmployeePaymentRecord.objects.get(employee=employee)
        commission_earned = all_employee_payment_record.total_commission

        if amount_paid > all_employee_payment_record.balance:
            message = 'Amount cannot be greater than the balance.'
            return render(request, 'realestates/confirm_employee_payment.html',
                          {'employee_id': employee_id, 'message': message})
        else:
            all_employee_payment_record.amount_paid += amount_paid
            all_employee_payment_record.save()
            # print(all_employee_payment_record.amount_paid)
            all_employee_payment_record.balance = commission_earned - all_employee_payment_record.amount_paid
            all_employee_payment_record.save()

        return redirect(reverse('realestates:admin_dashboard', args=[request.user.id]))

    # Handle GET requests if needed
    # For example, you might display a confirmation page for approval
    return render(request, 'realestates/confirm_employee_payment.html')


@login_required
def add_client(request):

    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            # print(client)
            employee = Employees.objects.get(user=request.user)
            # print(employee)
            client.employee = employee
            client.save()
            Payment.objects.create(client=client, amount_paid=0, employee=employee, approved=False)
            return redirect(reverse('realestates:employee_dashboard', args=[request.user.id]))
    else:
        form = ClientForm()
    return render(request, 'realestates/add_client.html', {'form': form})


@login_required
def client_list(request):

    admin_id = request.user.id
    admin = Employees.objects.get(id=request.user.id)
    profile_pic_url = admin.profile_pic.url
    company = Company.objects.get(id=1)
    company_logo_url = company.company_logo.url

    expiry_date = timezone.now().now().date() - timedelta(days=7)
    # Filter clients who have not exceeded the expiry date
    active_clients = Client.objects.filter(date__date__gte=expiry_date).order_by('-date')

    all_clients = active_clients

    # Handle search query
    query = request.GET.get('q')
    if query:
        all_clients = all_clients.filter(phoneNumber1__icontains=query)  # Adjust field ('name') based on search criteria
    # Apply pagination
    paginator = Paginator(all_clients, 50)  # Display 10 clients per page
    page_number = request.GET.get('page')
    try:
        clients = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        clients = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results
        clients = paginator.page(paginator.num_pages)

    context = {
        'clients': clients,
        'admin_id': admin_id,
        'company_logo_url': company_logo_url,
        'profile_pic_url': profile_pic_url,
    }

    return render(request, 'realestates/client_list.html', context)


@login_required
def UpdateClient(request, pk):

    client_info = get_object_or_404(Client, id=pk)

    if request.method == 'POST':
        client_form = ClientEditForm(data=request.POST, instance=client_info)
        if client_form.is_valid():
            client_form.save()
            return redirect(reverse('realestates:employee_dashboard', args=[request.user.id]))
    else:
        # Populate forms with existing data
        client_form = ClientEditForm(instance=client_info)

    return render(request, 'realestates/edit_client.html', {'form': client_form})


def email_message(semail, username,  type):
    if type == 'register':
        # print("0044444444444444")
        email_from = 'noreply@drbaranes.com'
        subject = 'Registering in Century Properties & Real Estates Ltd'
        body = 'You were registered. Temporal password: sql1pass and username: '+username +' Please login and Update/Edit your profile .' \
               'https://centuryproperties.pythonanywhere.com/'
        # print("005555555555555")

    send_mail(subject, body, email_from, [semail], fail_silently=False)


@login_required
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            semail = cd['email']
            username = cd['username']
            email_message(semail, username, 'register')
            form.save()
            return redirect(reverse('realestates:admin_dashboard', args=[request.user.id]))

    form = RegistrationForm()
    admin_id = request.user.id
    admin = Employees.objects.get(id=request.user.id)
    profile_pic_url = admin.profile_pic.url
    company = Company.objects.get(id=1)
    company_logo_url = company.company_logo.url
    employees = Employees.objects.all().filter(is_administrator=False)
    context = {
        'form': form,
        'admin_id': admin_id,
        'employees': employees,
        'company_logo_url': company_logo_url,
        'profile_pic_url': profile_pic_url,
    }

    return render(request, 'realestates/registration/reg_form.html', context)


def edit_user_profile_new(request):
    # company_obj = WebSiteCompany(request, web_company_id=7).site_company()
    profile = Employees.objects.filter(user=request.user)
    if not profile:
        profile = Employees.objects.create(user=request.user)
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.employee, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            if request.user.is_staff:  # Check if user is admin
                # return redirect('admin_dashboard')  # Redirect admin to admin dashboard
                # print(user)
                # print(user.id)
                return redirect(reverse('realestates:admin_dashboard', args=[request.user.id]))
            else:
                return redirect(reverse('realestates:employee_dashboard', args=[request.user.id]))
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.employee)
    return render(request, 'realestates/registration/edit_user_profile.html', {'user_form': user_form,
                                                                                        'profile_form': profile_form, })


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)
        for field in form:
            print("Field Error:", field.name, field.errors)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect(reverse('realestates:login_page'))
        else:
            print("Field Error:", field.name, field.errors)
            messages.error(request, field.errors)
            return redirect(reverse('realestates:change_password'))
    else:
        form = PasswordChangeForm(user=request.user)

        args = {'form': form}
        return render(request, 'realestates/registration/change_password.html', args)


class CustomLogoutView(View):
    def post(self, request):
        # Handle post request if needed
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('realestates:login_page')  # Adjust the redirect URL as needed

    def get(self, request):
       pass


def pending_payments_view(request):
    admin_id = request.user.id
    admin = Employees.objects.get(id=request.user.id)
    profile_pic_url = admin.profile_pic.url
    company = Company.objects.get(id=1)
    company_logo_url = company.company_logo.url
    employees = Employees.objects.all().filter(is_administrator=False)
    clients_with_pending_payments = Payment.objects.filter(remaining_amount__gt=0).all()

    context = {
        'clients_with_pending_payments': clients_with_pending_payments,
        'admin_id': admin_id,
        'employees': employees,
        'company_logo_url': company_logo_url,
        'profile_pic_url': profile_pic_url,
    }

    return render(request, 'realestates/installment_lists.html', context)


def truncate_model(request):
    # print('9015 params')
    # print(params)
    dic = request.POST['dic']
    print(dic)
    dic_ = eval(dic)
    app_ = dic_['app']
    model_name_ = dic_['model_name']
    try:
        model = apps.get_model(app_label=app_, model_name=model_name_)
        print(model)
        model.truncate()
    except Exception as ex:
        print("9025 " + str(ex))

    result = "Data truncated"
    return result