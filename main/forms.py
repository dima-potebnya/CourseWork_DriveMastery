from django.contrib.auth import get_user_model
from .models import *
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
import re

User = get_user_model()

fullname_validator=[
    RegexValidator(
        regex=r'^[A-Za-zА-Яа-яЁёІіЇїЄєҐґ\s]{25,40}+$',
        message='ПІБ може містити тільки букви, довжиною від 25 до 40 символів.',
        code='invalid_full_name'
    )
]
username_validator=[
    RegexValidator(
        regex=r'^[a-z0-9]{6,15}$',
        message='Логін може містити тільки латинські літери та цифри, довжиною від 6 до 15 символів.',
        code='invalid_username'
    )
]
def password_validator(value):
    if not re.match('^[a-zA-Z0-9]*$', value):
        raise ValidationError('Пароль повинен містити тільки цифри і букви латинського алфавіту.')
    if len(value) < 6:
        raise ValidationError('Пароль має містити не менше 6 символів.')
    if len(value) > 15:
        raise ValidationError('Пароль має містити не більше 15 символів.')
    if not any(char.isdigit() for char in value):
        raise ValidationError('Пароль має містити хоча б одну цифру.')
    if not any(char.isupper() for char in value):
        raise ValidationError('Пароль має містити хоча б одну літеру верхнього регістру латинського алфавіту.')
email_validator=[
    RegexValidator(
        regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        message='Введіть коректний email.',
        code='invalid_mail' 
    )
]
class RegistrationForm(forms.Form):
    full_name = forms.CharField(label='ПІБ', validators=fullname_validator)
    username = forms.CharField(label='Логін', validators=username_validator)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput, validators=[password_validator])
    confirm_password = forms.CharField(label='Повторіть пароль', widget=forms.PasswordInput)
    email = forms.CharField(label='E-mail', validators=email_validator)
    role = forms.ChoiceField(label='Роль', choices=[('student', 'Студент'),
                                                    ('teacher', 'Викладач'), 
                                                    ('moderator', 'Модератор'), 
                                                    ('admin', 'Адміністратор')])   
    category = forms.ChoiceField(label='Категорія', choices=[('A', 'A'), 
                                                             ('A1', 'A1'), 
                                                             ('B', 'B'), 
                                                             ('B1', 'B1'), 
                                                             ('C', 'C'), 
                                                             ('C1', 'C1')], required=False)    
    secret_admin_code = forms.CharField(label='Секретний код адміна', required=False)                                                             

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        if User.objects.filter(username=username).exists():
            raise ValidationError("Такий користувач вже існує")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("Такий Email вже існує")
        return email
        
    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Паролі не співпадають")      
        return password
        
    def clean_secret_admin_code(self):
        role = self.cleaned_data.get('role')
        secret_admin_code = self.cleaned_data.get('secret_admin_code')
        if role == 'admin' and secret_admin_code != settings.SECRET_ADMIN_CODE:
            raise ValidationError("Невірний секретний код адміна")
        return secret_admin_code
    
        
class AuthenticationForm(forms.Form):
    username = forms.CharField(label='Логін', max_length=15)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput, max_length=15) 

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise ValidationError('Невірний логін чи пароль')
        return cleaned_data    