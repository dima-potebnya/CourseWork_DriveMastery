from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, full_name, password=None):
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

class CustomUser(AbstractBaseUser):
    full_name = models.CharField(max_length=40)
    username = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    user_type_choices = [('student', 'Student'),
                         ('teacher', 'Teacher'),
                         ('moderator', 'Moderator'),
                         ('admin', 'Admin')
    ]
    user_type = models.CharField(max_length=10, choices=user_type_choices)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'full_name']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

class Admin(CustomUser):
    pass

class Moderator(CustomUser):
    pass

class Teacher(CustomUser):
    pass

class Student(CustomUser):
    category_choices = [('A', 'A'), 
                        ('A1', 'A1'), 
                        ('B', 'B'), 
                        ('B1', 'B1'), 
                        ('C', 'C'), 
                        ('C1', 'C1')
    ]
    category = models.CharField(max_length=2, choices=category_choices) 
