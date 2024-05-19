from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class CustomUserManager(BaseUserManager): # Менеджер для кастомного користувача
    def create_user(self, username, email, full_name, password=None): # Метод для створення користувача
        if not email:
            raise ValueError('The Email field must be set')
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            full_name=full_name
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    # Метод для створення суперкористувача
    def create_superuser(self, username, email, full_name, password=None):
        user = self.create_user(
            username=username,
            email=email,
            full_name=full_name,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser): # Кастомна модель користувача
    full_name = models.CharField(max_length=40) # Повне ім'я користувача
    username = models.CharField(max_length=15, unique=True) # Унікальне ім'я користувача
    email = models.EmailField(unique=True) # Унікальна email адреса
    is_active = models.BooleanField(default=True) # Чи активний користувач
    is_admin = models.BooleanField(default=False) # Чи є користувач адміністратором
    is_block = models.BooleanField(default=True) # Чи заблокований користувач
    user_type_choices = [('student', 'Student'),
                         ('teacher', 'Teacher'),
                         ('moderator', 'Moderator'),
                         ('admin', 'Admin')
    ] # Вибір типу користувача
    user_type = models.CharField(max_length=10, choices=user_type_choices) # Поле для зберігання типу користувача
    
    objects = CustomUserManager() # Вказуємо кастомний менеджер користувачів

    USERNAME_FIELD = 'username' # Поле, яке використовується для логіна
    REQUIRED_FIELDS = ['email', 'full_name'] # Обов'язкові поля

    def __str__(self): # Метод для представлення користувача у вигляді рядка
        return self.username

    def has_perm(self, perm, obj=None): # Метод для перевірки прав доступу
        return True

    def has_module_perms(self, app_label): # Метод для перевірки прав доступу до модулів
        return True

    @property
    def is_staff(self): # Властивість для перевірки, чи є користувач членом персоналу
        return self.is_admin

class Admin(CustomUser): # Модель адміністратора, наслідується від CustomUser
    pass

class Moderator(CustomUser): # Модель модератора, наслідується від CustomUser
    pass

class Teacher(CustomUser): # Модель викладача, наслідується від CustomUser
    pass

class Student(CustomUser): # Модель студента, наслідується від CustomUser
    pass

class Video(models.Model): # Модель відео
    title = models.CharField(max_length=200) # Назва відео
    description = models.TextField() # Опис відео
    video_file = models.FileField(upload_to='videos/') # Файл відео
    created_at = models.DateTimeField(auto_now_add=True) # Дата створення відео

    def __str__(self): 
        return self.title # Метод для представлення відео у вигляді рядка

class Question(models.Model): # Модель питання
    question_text = models.TextField() # Текст питання
    created_at = models.DateTimeField(auto_now_add=True) # Дата створення питання
 
    def __str__(self):
        return self.question_text # Метод для представлення питання у вигляді рядка

class Answer(models.Model): # Модель відповіді
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers') # Зв'язок з питанням
    answer_text = models.TextField() # Текст відповіді
    is_correct = models.BooleanField(default=False) # Чи є відповідь правильною

    def __str__(self):
        return self.answer_text # Метод для представлення відповіді у вигляді рядка

class Test(models.Model): # Модель тесту
    title = models.CharField(max_length=200) # Назва тесту
    description = models.TextField() # Опис тесту
    questions = models.ManyToManyField(Question) # Зв'язок з питаннями
    created_at = models.DateTimeField(auto_now_add=True) # Дата створення тесту

    def __str__(self):
        return self.title # Метод для представлення тесту у вигляді рядка