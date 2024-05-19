from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.check_user_root, name='check_user_root'),
    path('guest_main/', views.guest, name='guest'),  # URL для головної сторінки
    path('guest_main/about/', views.guest, name='about'),  # URL для сторінки про нас
    path('guest_main/contacts/', views.guest, name='contacts'),  # URL для сторінки контактів
    path('guest_main/login/', views.login_view, name='login'),  # URL для сторінки логіну
    path('guest_main/register/', views.register, name='register'),  # URL для сторінки реєстрації
    path('logout/', views.logout_view, name='logout'),
    
    path('admin_main/', views.admin, name='admin'),  # URL для сторінки адміна
    path('moderator_main/', views.moderator, name='moderator'), # URL для сторінки модератора
    path('teacher_main/', views.teacher, name='teacher'), # URL для сторінки вчителя
    path('student_main/', views.student, name='student'), # URL для сторінки студента
    
    path('update_profile/', views.update_profile, name='update_profile'), # URL для редагування профілю
    
    path('<str:user_type>_main/about/', views.main, name='about_main'),
    path('<str:user_type>_main/contacts/', views.main, name='contacts_main'),
    path('<str:users_type>_main/users/', views.users, name='users'),
    path('<str:user_type>_main/account/', views.account, name='account'),
    path('<str:user_type>_main/materials/', views.materials, name='materials'),
    path('<str:user_type>_main/take_test/<int:test_id>/', views.take_test, name='take_test'),
    
    path('<str:user_type>_main/videos/', views.video_list, name='video_list'),    
    path('<str:user_type>_main/videos/add/', views.video_edit, name='video_add'),
    path('<str:user_type>_main/videos/<int:video_id>/edit/', views.video_edit, name='video_edit'),
    path('<str:user_type>_main/videos/<int:video_id>/delete/', views.video_delete, name='video_delete'),
    
    path('<str:user_type>_main/tests/', views.test_list, name='test_list'),
    path('<str:user_type>_main/tests/add/', views.test_edit, name='test_add'),
    path('<str:user_type>_main/tests/<int:test_id>/edit/', views.test_edit, name='test_edit'),
    path('<str:user_type>_main/tests/<int:test_id>/delete/', views.test_delete, name='test_delete'),
    path('<str:user_type>_main/tests/<int:test_id>/question/', views.add_test_question, name='add_test_question'),
    path('<str:user_type>_main/tests/<int:test_id>/question/<int:question_id>/delete/', views.question_delete, name='question_delete'),
    path('<str:user_type>_main/tests/<int:test_id>/answers/<int:question_id>/', views.add_test_answers, name='add_test_answers'),  
    
    
]

# Обслуговування статичних файлів у режимі налагодження
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)