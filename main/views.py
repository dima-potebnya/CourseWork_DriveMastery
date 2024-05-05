from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import RegistrationForm,AuthenticationForm
from .models import *        
import json   
    
def index(request):
    if request.user.is_authenticated: # Проверка если пользователь вошёл (то перенаправляем его в его страницу)
        role = request.user.user_type  # Получаем роль пользователя
        return redirect(f'/{role}_main/')  # Перенаправляем на соответствующую страницу
    else: # Если не вошёл показываем содержимое главной страницы
        return main(request,'guest')  # Повертає шаблон administrator.html  

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
            if role == 'admin':
                blocked = False
            else:
                blocked = True
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
                    user_type=role,  # Присваиваем тип пользователя
                    is_block=blocked
                )
                
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
    return main(request,'admin')  # Повертає шаблон administrator.html
       
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
        show_users = request.GET.get('show', None)
        type_select = 'Адміни'
        found_users = False
        if show_users == 'admin':
            type_select = 'Адміни'
            found_users = context['users'].filter(user_type='admin').exists()
        elif show_users == 'moderator':
            type_select = 'Модератори'
            found_users = context['users'].filter(user_type='moderator').exists()
        elif show_users == 'teacher':
            type_select = 'Викладачі'
            found_users = context['users'].filter(user_type='teacher').exists()
        elif show_users == 'student':
            type_select = 'Студенти'
            found_users = context['users'].filter(user_type='student').exists()
        context['show_users'] = show_users
        context['type_select'] = type_select
        context['page_title'] = 'Користувачі'
        context['found_users'] = found_users
        if request.GET.get('profile'):
            profile_username = request.GET.get('profile')
            try:
                profile_user = CustomUser.objects.get(username=profile_username)
                context['show_content'] = 'profile'
                context['full_name'] = profile_user.full_name
                context['username'] = profile_user.username
                context['email'] = profile_user.email
                context['password'] = profile_user.password
                context['user_type'] = profile_user.user_type
                if profile_user.is_block:
                    context['is_block'] = 'Заблокований'
                elif not profile_user.is_block:
                    context['is_block'] = 'Розблокований'
                context['page_title'] = f"Профіль користувача {profile_user.full_name}"
                context['title'] = "Профіль користувача"
            except CustomUser.DoesNotExist:
            # Обработка случая, когда пользователь не найден
                pass
        if request.GET.get('unblock'):
            profile_username = request.GET.get('unblock')
            profile_user = CustomUser.objects.get(username=profile_username)
            profile_user.is_block = False
            profile_user.save()  # Сохраняем изменения в базе данных
            return redirect(reverse('users') + f'?show={profile_user.user_type}')
        if request.GET.get('block'):
            profile_username = request.GET.get('block')
            profile_user = CustomUser.objects.get(username=profile_username)
            profile_user.is_block = True
            profile_user.save()  # Сохраняем изменения в базе данных
            return redirect(reverse('users') + f'?show={profile_user.user_type}')
        if request.GET.get('delete'):
            profile_username = request.GET.get('delete')
            profile_user = CustomUser.objects.get(username=profile_username)
            profile_user.delete()  # Удаляем пользователя из базы данных
            return redirect(reverse('users') + f'?show={profile_user.user_type}')
        if request.GET.get('new_user'):
            context['show_content'] = 'new_user'
            context['page_title'] = 'Новий користувач'
            if request.method == 'POST':
                form = RegistrationForm(request.POST)
                if form.is_valid():
                    full_name = form.cleaned_data['full_name']
                    username = form.cleaned_data['username']
                    password = form.cleaned_data['password']
                    email = form.cleaned_data['email']
                    role = form.cleaned_data['role']
                    if role == 'admin':
                        blocked = False
                    else:
                        blocked = True
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
                            user_type=role,  # Присваиваем тип пользователя
                            is_block=blocked
                        )
                
                        # Сохраняем профиль пользователя
                        user_profile.save()           
            
                    # Перенаправляем на исходную страницу
                    return redirect(reverse('users') + f'?show=student')
            else:
                form = RegistrationForm()
            context['form'] = form  # Добавляем форму в контекст, чтобы передать ее в шаблон
    elif request.path == f'/{user}_main/account/': # Сторінка Мій профіль
        context['show_content'] = 'account'
        context['full_name'] = request.user.full_name
        context['username'] = request.user.username
        context['email'] = request.user.email
        context['password'] = request.user.password
        context['user_type'] = request.user.user_type
        if request.user.is_block:
            context['is_block'] = 'Заблокований'
        elif not request.user.is_block:
            context['is_block'] = 'Розблокований'
        context['page_title'] = f"Ваш профіль {request.user.full_name}"
        context['title'] = "Ваш профіль"
        
        
    if user=='admin':user='administrator'
    if user=='guest':user='index'
    return render(request, f'main/{user}.html', context)   
    
def check_user_role_and_redirect(request, expected_role):
    if request.user.is_authenticated:  # Проверяем, аутентифицирован ли пользователь
        role = request.user.user_type  # Получаем роль пользователя
        if role != expected_role:  # Если роль пользователя не соответствует ожидаемой
            return redirect(f'/{role}_main/')  # Перенаправляем на соответствующую страницу
    else:
        return redirect('/guest_main/')  # Если пользователь не аутентифицирован, перенаправляем на главную страницу для гостей    
        
@login_required
def update_profile(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        full_name = data.get('full_name')
        username = data.get('login')
        email = data.get('email')
        password = data.get('password')
        
        user = CustomUser.objects.get(username=data.get('old_login'))

        if full_name:
            user.full_name = full_name
        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.password = make_password(password)

        try:
            user.full_clean()
            user.save()
            return JsonResponse({'success': True})
        except ValidationError as e:
            error_dict = {}
            for field, errors in e.message_dict.items():
                error_dict[field] = [str(error) for error in errors]
            return JsonResponse({'success': False, 'error': error_dict})

    else:
        return JsonResponse({'success': False, 'error': 'Невірний метод запиту'})