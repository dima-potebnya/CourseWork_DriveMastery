from django.contrib.auth import get_user_model
from .models import *
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
import re

User = get_user_model() # Отримання користувацької моделі

fullname_validator=[ # Валідатор для ПІБ користувача
    RegexValidator(
        regex=r'^[A-Za-zА-Яа-яЁёІіЇїЄєҐґ\s]{16,40}+$', # Регулярний вираз для перевірки ПІБ
        message='ПІБ може містити тільки букви, довжиною від 16 до 40 символів.', # Повідомлення про помилку
        code='invalid_full_name' # Код помилки
    )
]
username_validator=[ # Валідатор для логіну користувача
    RegexValidator(
        regex=r'^[a-z0-9]{6,15}$', # Регулярний вираз для перевірки логіну
        message='Логін може містити тільки латинські літери та цифри, довжиною від 6 до 15 символів.', # Повідомлення про помилку
        code='invalid_username' # Код помилки
    )
]
def password_validator(value): # Функція валідатора для пароля
    if not re.match('^[a-zA-Z0-9]*$', value): # Перевірка чи пароль містить тільки цифри і букви латинського алфавіту
        raise ValidationError('Пароль повинен містити тільки цифри і букви латинського алфавіту.')
    if len(value) < 6: # Перевірка довжини пароля (не менше 6 символів)
        raise ValidationError('Пароль має містити не менше 6 символів.')
    if len(value) > 15: # Перевірка довжини пароля (не більше 15 символів)
        raise ValidationError('Пароль має містити не більше 15 символів.')
    if not any(char.isdigit() for char in value): # Перевірка наявності хоча б однієї цифри у паролі
        raise ValidationError('Пароль має містити хоча б одну цифру.')
    if not any(char.isupper() for char in value): # Перевірка наявності хоча б однієї літери верхнього регістру у паролі
        raise ValidationError('Пароль має містити хоча б одну літеру верхнього регістру латинського алфавіту.')
email_validator=[ # Валідатор для email
    RegexValidator(
        regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', # Регулярний вираз для перевірки email
        message='Введіть коректний email.', # Повідомлення про помилку
        code='invalid_mail' # Код помилки
    )
]
class RegistrationForm(forms.Form): # Форма реєстрації користувача
    full_name = forms.CharField(label='ПІБ', validators=fullname_validator) # Поле для ПІБ
    username = forms.CharField(label='Логін', validators=username_validator) # Поле для логіну
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput, validators=[password_validator]) # Поле для пароля
    confirm_password = forms.CharField(label='Повторіть пароль', widget=forms.PasswordInput) # Поле для підтвердження пароля
    email = forms.CharField(label='E-mail', validators=email_validator) # Поле для email
    role = forms.ChoiceField(label='Роль', choices=[('student', 'Студент'), # Поле для вибору ролі
                                                    ('teacher', 'Викладач'), 
                                                    ('moderator', 'Модератор'), 
                                                    ('admin', 'Адміністратор')])      
    secret_admin_code = forms.CharField(label='Секретний код адміна', required=False) # Поле для секретного коду адміна                                                             

    def clean_username(self): # Перевірка унікальності логіну
        username = self.cleaned_data['username'].lower()
        if User.objects.filter(username=username).exists():
            raise ValidationError("Такий користувач вже існує")
        return username

    def clean_email(self): # Перевірка унікальності email
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("Такий Email вже існує")
        return email
        
    def clean_confirm_password(self): # Перевірка збігу паролів
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Паролі не співпадають")      
        return password
        
    def clean_secret_admin_code(self): # Перевірка правильності секретного коду адміна
        role = self.cleaned_data.get('role')
        secret_admin_code = self.cleaned_data.get('secret_admin_code')
        if role == 'admin' and secret_admin_code != settings.SECRET_ADMIN_CODE:
            raise ValidationError("Невірний секретний код адміна")
        return secret_admin_code
        
class AuthenticationForm(forms.Form): # Форма аутентифікації користувача
    username = forms.CharField(label='Логін', max_length=15) # Поле для логіну
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput, max_length=15) # Поле для пароля

    def clean(self): # Перевірка правильності логіну та пароля
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise ValidationError('Невірний логін чи пароль')
        if user.is_block:
            raise ValidationError("Ваш обліковий запис заблокований або ще не підтверджений")
        return cleaned_data  

class VideoForm(forms.ModelForm): # Форма для відео
    video_file = forms.FileField(label='Файл відео') # Поле для файлу відео
    class Meta:
        model = Video
        fields = ['title', 'description', 'video_file']  # Поля форми      
        labels = {
            'title': 'Заголовок', # Мітка для поля "title"
            'description': 'Опис', # Мітка для поля "description"
            'video_file': 'Файл відео' # Мітка для поля "video_file"
        }

class TestForm(forms.ModelForm): # Форма для тесту
    class Meta:
        model = Test
        fields = ['title', 'description'] # Поля форми
        labels = {
            'title': 'Заголовок', # Мітка для поля "title"
            'description': 'Опис', # Мітка для поля "description"
        }
        
class QuestionForm(forms.ModelForm): # Форма для запитання
    class Meta:
        model = Question
        fields = ['question_text'] # Поля форми
        labels = {
            'question_text': 'Запитання' # Мітка для поля "question_text"
        }

class AnswerForm(forms.ModelForm): # Форма для відповіді
    class Meta:
        model = Answer
        fields = ['answer_text', 'is_correct'] # Поля форми   
        labels = {
            'answer_text': 'Відповідь', # Мітка для поля "answer_text"
            'is_correct': 'Вірна' # Мітка для поля "is_correct"
        }        