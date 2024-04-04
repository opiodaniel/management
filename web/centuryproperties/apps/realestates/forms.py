from django import forms
from .models import Client
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import (UserCreationForm)
from django.contrib.auth import get_user_model
from .models import (Employees)
from django.contrib.auth.models import User

#class loginForm(forms.ModelForm):
    #class Meta:
        #model = Login
        #fields = "__all__"


class ClientForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    phoneNumber1 = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    phoneNumber2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'required': False}))
    location = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Client
        fields = (
            'name',
            'phoneNumber1',
            'phoneNumber2',
            'location',
            # 'date',
        )

    def clean_phoneNumber1(self):
        phone_number1 = self.cleaned_data['phoneNumber1']
        print('phone_number1', phone_number1)
        if Client.objects.filter(phoneNumber1=phone_number1).exists():
            raise forms.ValidationError('A client with the same phone number already exist')
        return phone_number1

    def clean_phoneNumber2(self):
        phone_number2 = self.cleaned_data['phoneNumber2']
        print('phone_number2', phone_number2)
        if not phone_number2:
            print('am empty')
            return phone_number2
        else:
            if len(phone_number2) < 10:
                raise forms.ValidationError("Phone number must be at least 10 characters long.")
            if Client.objects.filter(phoneNumber2=phone_number2).exists():
                raise forms.ValidationError('A client with the same phone number already exists')
        return phone_number2


class EmployeeLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.Field(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose a different one.")
        return username

    class Meta:
        model = get_user_model()
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        )

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user

    class LoginForm(AuthenticationForm):
        password = forms.CharField(widget=forms.PasswordInput)


class UserEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = (
            'first_name',
            'last_name',
            'email'
        )


class ProfileEditForm(forms.ModelForm):
    date_of_birth = forms.CharField(widget=forms.TextInput(attrs={'type': 'date'}))

    class Meta:
        model = Employees
        fields = ('profile_pic', 'date_of_birth', 'short_bio', 'bio',
                  'address', 'zip', 'city', 'country',
                  'phone',)


class MessageForm(forms.Form):
    recipient = forms.ModelChoiceField(queryset=Employees.objects.all())
    subject = forms.CharField(max_length=100)
    content = forms.CharField(widget=forms.Textarea)