from django.shortcuts import render, redirect,  get_object_or_404

from django.contrib import messages
from django.contrib.auth.models import User,auth

from .models import Client, Employees, Payment, MonthlyTotal, TotalAmount, Company
from .forms import ClientForm, EmployeeLoginForm, RegistrationForm, ProfileEditForm, UserEditForm

from django.contrib.auth import authenticate, login

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from django.core.mail import send_mail

from datetime import date

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
#Home page


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

    # Print or use the total amounts
    # print("Total amount made today:", total_amount_made_today)
    # print("Total amount made in previous days:", total_amount_previous_days)

    total_sale_for_today_previous_days = total_amount_made_today + total_amount_previous_days

    # today = date.today()
    # # Query the TotalAmount model for the total amount made today
    # total_amount_today_ = TotalAmount.objects.filter(date=today).first()
    #
    # print(total_amount_today_)
    # if total_amount_today_ is None:
    #     total_amount_today_ = 0
    # print(total_amount_today_)

    admin = Employees.objects.get(id=admin_id)
    employees = Employees.objects.filter(is_administrator=False)

    payments = Payment.objects.filter(approved=False).order_by('approved', '-client__date')
    total_number_clients = Client.objects.all().count

    clients = Client.objects.all().count()
    profile_pic_url = admin.profile_pic.url

    approved_clients = []
    appending_clients = []
    for e in employees:
        # print('employee ', e.total_approved_clients())
        approved_client = e.total_approved_clients()
        approved_clients.append(approved_client)
        appending_client = e.total_appending_clients()
        appending_clients.append(appending_client)
        clients_ = Client.objects.filter(employee=e)
        for c in clients_:
            pass
            # print('employee ', e,  c)
            # appending_clients.append(c)
    total_number_of_approved_clients = sum(approved_clients)
    # print("total_number_of_approved_clients ==", total_number_of_approved_clients)
    total_number_of_appending_clients = sum(appending_clients)
    # print("total_number_of_appending_clients ==", total_number_of_appending_clients)
    total_num_clients_ = Client.objects.all().count()
    # print("total_num_clients_ ==", total_num_clients_)
    total_number_employees = Employees.objects.filter(is_administrator=False).count()
    # print("total_num_employees_ ==", total_number_employees)

    context = {
        'employee': admin,
        'admin_id': admin_id,
        'profile_pic_url': profile_pic_url,
        'clients': clients,
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
    clients = employee.client_employee.all()

    approved_clients_count = Payment.objects.filter(employee_id=employee_id, approved=True).count()
    print(approved_clients_count)
    pending_clients_count = Payment.objects.filter(employee_id=employee_id, approved=False).count()
    print(pending_clients_count)

    context = {
        'employee': employee,
        'profile_pic_url': profile_pic_url,
        # 'total_weekly_commission': total_weekly_commission,
        'clients': clients,
        'total_number_of_clients': total_number_of_clients,
        'total_approved_clients': total_approved_clients,
        'total_appending_clients': total_appending_clients,
        'payments': payments,
        'company_logo_url': company_logo_url,
        'employee_payment_record': employee_payment_record,
    }

    # Render the employee dashboard template
    return render(request, 'realestates/employee_dashboard.html', context)


def employees_client(request):
    employees = Employees.objects.filter(is_administrator=False)
    dic_ = {}

    for employee in employees:
        approved_clients = Payment.objects.filter(employee=employee, approved=True).count()
        appending_clients = Payment.objects.filter(employee=employee, approved=False).count()

        employee_clients = []
        for payment in Payment.objects.filter(employee=employee):
            client_dict = {
                'id': payment.client.id,
                'name': payment.client.name,
                # Add other client fields as needed
            }
            employee_clients.append(client_dict)

        dic_[employee.user.username] = {
            'approved_clients': approved_clients,
            'appending_clients': appending_clients,
            'clients': employee_clients
        }
    return JsonResponse(dic_)


def approve_payment(request, client_id):
    # print(client_id)
    payment_client_id = client_id
    client = Client.objects.get(id=client_id)
    context = {
        'payment_client_id': payment_client_id,
        'client': client,
    }
    return render(request, 'realestates/confirm_client_payment.html', context)


@transaction.atomic
def confirm_payment(request, client_id):
    if request.method == 'POST':
        # Get the amount paid from the form data
        amount_paid_str = request.POST.get('amount_paid', '0').replace(',', '')  # Remove commas
        amount_paid = int(amount_paid_str)
        if amount_paid <= 0:
            message = 'You must enter a valid positive amount.'
            return render(request, 'realestates/confirm_client_payment.html', {'payment_client_id': client_id, 'message':message})
        else:
            # Assuming the request.user is the user making the request
            current_user = request.user

            # Check if the current user is a superuser (admin)
            if current_user.is_superuser:
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
                payment.amount_paid = amount_paid
                payment.timestamp = date.today()
                payment.approved = True
                payment.approved_by = admin_employee
                payment.save()

                # Calculate commission for non-admin employees and update EmployeePaymentRecord
                for employee in Employees.objects.filter(is_administrator=False):
                    all_employee_payment_record = EmployeePaymentRecord.objects.get(employee=employee)
                    all_employee_payment_record.total_commission = employee.calculate_weekly_commission()
                    all_employee_payment_record.balance = employee.calculate_weekly_commission()-all_employee_payment_record.amount_paid
                    all_employee_payment_record.save()

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


def pay_employee(request):

    admin = Employees.objects.get(id=request.user.id)
    profile_pic_url = admin.profile_pic.url
    company = Company.objects.get(id=1)
    company_logo_url = company.company_logo.url
    employees = Employees.objects.all().filter(is_administrator=False)
    all_employee_payment_record = EmployeePaymentRecord.objects.filter(employee__in=employees)
    context = {
        'employees': employees,
        'company_logo_url': company_logo_url,
        'profile_pic_url': profile_pic_url,
        'all_employee_payment_record': all_employee_payment_record,
    }

    return render(request, 'realestates/pay_employee.html', context)


def approve_employee_payment(request, employee_id):
    employee_id_ = employee_id
    employee = Employees.objects.get(id=employee_id)
    context = {
        'employee_id': employee_id_,
        'employee': employee,
    }
    return render(request, 'realestates/confirm_employee_payment.html', context)


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


        # # Calculate balance
        # employee_balance = commission_earned - amount_paid
        # # Update EmployeePaymentRecord
        # all_employee_payment_record = EmployeePaymentRecord.objects.get(employee=employee)
        # all_employee_payment_record.amount_paid += amount_paid
        # all_employee_payment_record.balance = employee_balance
        # all_employee_payment_record.save()

        return redirect(reverse('realestates:admin_dashboard', args=[request.user.id]))

    # Handle GET requests if needed
    # For example, you might display a confirmation page for approval
    return render(request, 'realestates/confirm_employee_payment.html')


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


def email_message(semail, username,  type):
    if type == 'register':
        # print("0044444444444444")
        email_from = 'noreply@drbaranes.com'
        subject = 'Registering in Century Properties & Real Estates Ltd'
        body = 'You were registered. Temporal password: sql1pass and username: '+username+ ' date-format:1998-12-28 ' + 'Please login and Update/Edit your profile .' \
               'http://52.90.82.86/'
        # print("005555555555555")

    send_mail(subject, body, email_from, [semail], fail_silently=False)


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
    else:
        form = RegistrationForm()
    return render(request, 'realestates/registration/reg_form.html', {'form': form})


def login_page(request):
    if request.method == "POST":
        form_login = EmployeeLoginForm(request, data=request.POST)
        if form_login.is_valid():
            username = form_login.cleaned_data.get('username')
            password = form_login.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:  # Check if user is admin
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
        else:
            messages.error(request, "Invalid username or password.")
    return login_form_(request, error_message='')


def login_form_(request, error_message=''):

    form_login = EmployeeLoginForm()
    company = Company.objects.get(id=1)
    company_logo_url = company.company_logo.url

    arg = {'form_login': form_login,
           'error_message': error_message,
           'company_logo_url': company_logo_url
           }
    return render(request, 'realestates/registration/login.html', arg)


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
            if request.user.is_superuser:  # Check if user is admin
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