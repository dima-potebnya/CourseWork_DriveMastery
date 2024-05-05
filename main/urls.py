from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('', views.redirect_authenticated_user, name='redirect_authenticated_user'),
    path('guest_main/', views.index, name='guest'),  # URL для головної сторінки
    path('guest_main/about/', views.index, name='about'),  # URL для сторінки про нас
    path('guest_main/contacts/', views.index, name='contacts'),  # URL для сторінки контактів
    path('guest_main/login/', views.login_view, name='login'),  # URL для сторінки логіну
    path('guest_main/register/', views.register, name='register'),  # URL для сторінки реєстрації
    path('logout/', views.logout_view, name='logout'),
    
    path('admin_main/', views.administrator, name='administrator'),
    path('admin_main/about/', views.administrator, name='about_main'),
    path('admin_main/contacts/', views.administrator, name='contacts_main'),
    path('admin_main/users/', views.administrator, name='users'),
    path('admin_main/account/', views.administrator, name='account'),
    
    path('moderator_main/', views.moderator, name='moderator'),
    path('teacher_main/', views.teacher, name='teacher'),
    path('student_main/', views.student, name='student'),
    
    path('update_profile/', views.update_profile, name='update_profile')
]
