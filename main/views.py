from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegistrationForm,AuthenticationForm
from .models import *           
    
def index(request):
    if request.user.is_authenticated: # Проверка если пользователь вошёл (то перенаправляем его в его страницу)
        role = request.user.user_type  # Получаем роль пользователя
        return redirect(f'/{role}_main/')  # Перенаправляем на соответствующую страницу
    else: # Если не вошёл показываем содержимое главной страницы
        context = main(request,'guest')
        return render(request, 'main/index.html', context)  # Повертає шаблон administrator.html  

def redirect_authenticated_user(request):
    if request.user.is_authenticated:
        role = request.user.user_type  # Получаем роль пользователя
        return redirect(f'/{role}_main/')  # Перенаправляем на соответствующую страницу
    else:
        return redirect('/guest_main/')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']
            category = form.cleaned_data.get('category')
            
            # Хеширования пароля
            hashed_password = make_password(password)
            
            # Словарь для связи роли с соответствующей моделью
            role_model_map = {
                'student': Student, 
                'teacher': Teacher,  
                'moderator': Moderator,
                'admin': Admin                
            }
            
            # Проверяем, существует ли роль в карте моделей
            if role in role_model_map:
                # Получаем соответствующую модель из карты
                model = role_model_map[role]                
                
                # Создаем новый профиль пользователя
                user_profile = model.objects.create(
                    full_name=full_name,
                    username=username,
                    password=hashed_password,
                    email=email,
                    user_type=role  # Присваиваем тип пользователя
                )
                
                # Если роль студента, добавляем категорию
                if role == 'student':
                    user_profile.category = category
                
                # Сохраняем профиль пользователя
                user_profile.save()           
            
            # Перенаправляем на страницу авторизации
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'main/register.html', {'form': form})
    
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                user_type = user.user_type
                model_url_map = {
                    'admin': 'administrator',
                    'moderator': 'moderator',
                    'teacher': 'teacher',
                    'student': 'student',
                }
                if user_type in model_url_map:
                    url_name = model_url_map[user_type]
                    return redirect(url_name)
            else: #"Неправильний логін"
                return redirect('login')  # Redirect back to login page
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})   
    
def administrator(request):
    # Проверяем роль пользователя и перенаправляем его, если это другой пользователь
    redirect_result = check_user_role_and_redirect(request, 'admin')
    if redirect_result:
        return redirect_result
    context = main(request,'admin')
    return render(request, 'main/administrator.html', context)  # Повертає шаблон administrator.html
       
def moderator(request):
    # Проверяем роль пользователя и перенаправляем его, если это другой пользователь
    redirect_result = check_user_role_and_redirect(request, 'moderator')
    if redirect_result:
        return redirect_result
    return render(request, 'main/moderator.html')  # Повертає шаблон moderator.html

def teacher(request):
    # Проверяем роль пользователя и перенаправляем его, если это другой пользователь
    redirect_result = check_user_role_and_redirect(request, 'teacher')
    if redirect_result:
        return redirect_result
    return render(request, 'main/teacher.html')  # Повертає шаблон teacher.html

def student(request):
    # Проверяем роль пользователя и перенаправляем его, если это другой пользователь
    redirect_result = check_user_role_and_redirect(request, 'student')
    if redirect_result:
        return redirect_result
    return render(request, 'main/student.html')  # Повертає шаблон student.html  

def logout_view(request):
    logout(request)
    return redirect('/')  # Перенаправление на index.html после выхода    
    
def main(request, user): # Функція відображення сторінок
    page_title = "Ласкаво просимо до DriveMastery"
    image_url = "/static/png/autoschool.png"
    about_content = "Ми команда DriveMastery, яка працює для того, щоб надати вам найкращі послуги в галузі автомобільного навчання та підготовки. Наша місія - зробити водіння безпечним і комфортним для кожного. Ми пропонуємо широкий спектр послуг, від підготовки новачків до водіння до професійної підготовки водіїв важких транспортних засобів. З нами ви зможете вивчити та отримати всю необхідну інформацію про правила дорожнього руху, безпеку на дорогах та особливості керування різними типами автомобілів. Не соромтеся звертатися до нас за допомогою або консультацією - ми завжди готові допомогти вам!"
    contacts_content = "Телефон: +123456789\nEmail: example@example.com\nАдреса: вул. Прикладна, 123"

    context = {
        'page_title': page_title,
        'image_url': image_url,
        'about_content': about_content,
        'contacts_content': contacts_content,
    }

    # Определяем, какой контент отображать на основе URL
    if request.path == f'/{user}_main/':
        context['show_content'] = 'index_main'
    elif request.path == f'/{user}_main/about/':
        context['show_content'] = 'about_main'
        context['page_title'] = 'Про нас'
    elif request.path == f'/{user}_main/contacts/':
        context['show_content'] = 'contacts_main'
        context['page_title'] = 'Контакти' 
    elif request.path == f'/{user}_main/users/': # Сторінка Користувачі
        context['users'] = CustomUser.objects.all()
        context['show_content'] = 'users'
        context['page_title'] = 'Користувачі'
    return context    
    
def check_user_role_and_redirect(request, expected_role):
    if request.user.is_authenticated:  # Проверяем, аутентифицирован ли пользователь
        role = request.user.user_type  # Получаем роль пользователя
        if role != expected_role:  # Если роль пользователя не соответствует ожидаемой
            return redirect(f'/{role}_main/')  # Перенаправляем на соответствующую страницу
    else:
        return redirect('/guest_main/')  # Если пользователь не аутентифицирован, перенаправляем на главную страницу для гостей    