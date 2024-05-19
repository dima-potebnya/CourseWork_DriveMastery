from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from .forms import *
from .models import *        
import json   
    
def guest(request): # Функція головної сторінки гостя
    if request.user.is_authenticated: # Перевірка якщо користувач увійшов (то перенаправляємо його на його сторінку)
        role = request.user.user_type  # Отримуємо роль користувача
        return redirect(f'/{role}_main/')  # Перенаправляємо на відповідну сторінку
    else: # Якщо не увійшов показуємо вміст головної сторінки
        return main(request,'guest')

def check_user_root(request): # Функція перевірки користувача і перенаправлення на відповідну сторінку
    if request.user.is_authenticated: # Перевірка якщо користувач увійшов (то перенаправляємо його на його сторінку)
        role = request.user.user_type  # Отримуємо роль користувача
        return redirect(f'/{role}_main/')  # Перенаправляємо на відповідну сторінку
    else: # Якщо не увійшов перенаправляємо на сторінку гостя
        return redirect('/guest_main/')

def register(request): # Функція реєстрації
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']
            if role == 'admin': # При реєстрації автоматично блокуємо всіх окрім адміна
                blocked = False
            else:
                blocked = True
            # Хешування паролю
            hashed_password = make_password(password)
            
            # Словник для зв'язку ролі з відповідною моделлю
            role_model_map = {
                'student': Student, 
                'teacher': Teacher,  
                'moderator': Moderator,
                'admin': Admin                
            }
            
            # Перевіряємо, чи існує роль у карті моделей
            if role in role_model_map:
                # Отримуємо відповідну модель із карти
                model = role_model_map[role]                
                
                # Створюємо новий профіль користувача
                user_profile = model.objects.create(
                    full_name=full_name,
                    username=username,
                    password=hashed_password,
                    email=email,
                    user_type=role,  # Присвоюємо тип користувача
                    is_block=blocked
                )
                
                # Зберігаємо профіль користувача
                user_profile.save()           
            
            # Перенаправляємо на сторінку авторизації
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'main/register.html', {'form': form})
    
def login_view(request): # Функція авторизації
    if request.method == 'POST':
        form = AuthenticationForm(request.POST) # Хаваємо форму
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password) # Пробуємо автентифікувати
            if user is not None:
                login(request, user) # Записуємо сесію для користувача
                return redirect(user.user_type)
            else: #"Неправильний логін"
                return redirect('login')  # Перенаправлення на сторінку входу
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})   

@login_required    
def admin(request): # Функція адміна
    # Перевіряємо, чи є роль користувача дозволеною
    if request.user.user_type not in ['admin']:
        return HttpResponseForbidden()
    return main(request,'admin')  # Повертає шаблон admin.html

@login_required       
def moderator(request): # Функція модератора
    # Перевіряємо, чи є роль користувача дозволеною
    if request.user.user_type not in ['moderator']:
        return HttpResponseForbidden()
    return main(request, 'moderator')  # Повертає шаблон moderator.html

@login_required 
def teacher(request): # Функція викладача
    # Перевіряємо, чи є роль користувача дозволеною
    if request.user.user_type not in ['teacher']:
        return HttpResponseForbidden()
    return main(request, 'teacher')  # Повертає шаблон teacher.html

@login_required 
def student(request): # Функція студента
    # Перевіряємо, чи є роль користувача дозволеною
    if request.user.user_type not in ['student']:
        return HttpResponseForbidden()
    return main(request, 'student')  # Повертає шаблон student.html  

@login_required 
def logout_view(request): # Функція виходу
    logout(request)
    return redirect('/')  # Перенаправлення на guest.html після виходу  
    
def main(request, user_type): # Функція основної інформації
    page_title = "Ласкаво просимо до DriveMastery"
    image_url = "/static/png/autoschool.png"
    about_content = "Ми команда DriveMastery, яка працює для того, щоб надати вам найкращі послуги в галузі автомобільного навчання та підготовки. Наша місія - зробити водіння безпечним і комфортним для кожного. Ми пропонуємо широкий спектр послуг, від підготовки новачків до водіння до професійної підготовки водіїв важких транспортних засобів. З нами ви зможете вивчити та отримати всю необхідну інформацію про правила дорожнього руху, безпеку на дорогах та особливості керування різними типами автомобілів. Не соромтеся звертатися до нас за допомогою або консультацією - ми завжди готові допомогти вам!"
    contacts_content = "Телефон: +123456789\nEmail: example@example.com\nАдреса: вул. Прикладна, 123"

    context = {
        'page_title': page_title,
        'image_url': image_url,
        'about_content': about_content,
        'contacts_content': contacts_content
    }
    # Визначаємо, який контент відображати на основі URL
    if request.path == f'/{user_type}_main/':
        context['show_content'] = 'index_main'
    elif request.path == f'/{user_type}_main/about/':
        context['show_content'] = 'about_main'
        context['page_title'] = 'Про нас'
    elif request.path == f'/{user_type}_main/contacts/':
        context['show_content'] = 'contacts_main'
        context['page_title'] = 'Контакти' 
    return render(request, f'main/{user_type}.html', context)   
    
@login_required
def update_profile(request): # Функція "оновити профіль"
    if request.method == 'POST':
        data = json.loads(request.body)
        full_name = data.get('full_name')
        username = data.get('login')
        email = data.get('email')
        password = data.get('password')
        
        user = CustomUser.objects.get(username=data.get('old_login'))
        # Покрокова перевірка існуючих змін
        if full_name:
            user.full_name = full_name
        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.password = make_password(password)

        try:
            user.full_clean() # Оновлення даних
            user.save() # Збереження
            return JsonResponse({'success': True})
        except ValidationError as e: # Якщо помилка, то передаємо її
            error_dict = {}
            for field, errors in e.message_dict.items():
                error_dict[field] = [str(error) for error in errors]
            return JsonResponse({'success': False, 'error': error_dict})

    else:
        return JsonResponse({'success': False, 'error': 'Невірний метод запиту'})

@login_required
def users(request, users_type): # Функція "користувачі"
    # Перевіряємо, чи є роль користувача дозволеною
    if users_type not in ['admin', 'teacher']:
        return HttpResponseForbidden()
    user_types_mapping = {
        'admin': 'Адміни',
        'moderator': 'Модератори',
        'teacher': 'Викладачі',
        'student': 'Студенти'
    }
    if users_type == 'teacher': # Дозволяємо вчителю керувати тільки студентами
        show_users = 'student'
    else: # Або ж якщо адмін то усіма
        show_users = request.GET.get('show', None)
    type_select = None
    users = CustomUser.objects.all()
    if show_users in user_types_mapping:
        type_select = user_types_mapping[show_users] # Вивід укр інформації хто це
        found_users = users.filter(user_type=show_users).exists() # Змінна перевірки існування записів у БД
    else:
        found_users = False
    context = {
        'users': users,
        'show_content': 'users',
        'show_users': show_users,
        'type_select': type_select,
        'page_title': 'Користувачі',
        'found_users': found_users
    }
    if request.GET.get('profile'): # Якщо нажали на "Профіль"
        profile_username = request.GET.get('profile')
        profile_user = CustomUser.objects.get(username=profile_username)           
        context = {
            'show_content': 'profile',
            'full_name': profile_user.full_name,
            'username': profile_user.username,
            'email': profile_user.email,
            'password': profile_user.password,
            'user_type': profile_user.user_type,
            'page_title': f"Профіль користувача {profile_user.full_name}",
            'title': "Профіль користувача"
        }
        if profile_user.is_block: # Якщо користувач заблокований
            context['is_block'] = 'Заблокований'
        elif not profile_user.is_block:
            context['is_block'] = 'Розблокований'           
    if request.GET.get('unblock'): # Можливість розблокувати
        profile_username = request.GET.get('unblock')
        profile_user = CustomUser.objects.get(username=profile_username)
        profile_user.is_block = False
        profile_user.save()  # Зберігаємо зміни в базі даних
        return redirect(reverse('users', kwargs={'users_type': users_type}) + f'?show={profile_user.user_type}')
    if request.GET.get('block'): # Можливість заблокувати
        profile_username = request.GET.get('block')
        profile_user = CustomUser.objects.get(username=profile_username)
        profile_user.is_block = True
        profile_user.save()  # Зберігаємо зміни в базі даних
        return redirect(reverse('users', kwargs={'users_type': users_type}) + f'?show={profile_user.user_type}')
    if request.GET.get('delete'): # Можливість видалити
        profile_username = request.GET.get('delete')
        profile_user = CustomUser.objects.get(username=profile_username)
        profile_user.delete()  # Видаляємо користувача з бази даних
        return redirect(reverse('users', kwargs={'users_type': users_type}) + f'?show={profile_user.user_type}')
    if request.GET.get('new_user'): # Можливість додати нового користувача з адмін/викладач панелі
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
                # Хешування пароля
                hashed_password = make_password(password)
        
                # Словник для зв'язку ролі з відповідною моделлю
                role_model_map = {
                    'student': Student, 
                    'teacher': Teacher,  
                    'moderator': Moderator,
                    'admin': Admin                
                }
        
                # Перевіряємо, чи існує роль у карті моделей
                if role in role_model_map:
                    # Отримуємо відповідну модель із карти
                    model = role_model_map[role]                
            
                    # Створюємо новий профіль користувача
                    user_profile = model.objects.create(
                        full_name=full_name,
                        username=username,
                        password=hashed_password,
                        email=email,
                        user_type=role,  # Присвоюємо тип користувача
                        is_block=blocked
                    )
            
                    # Зберігаємо профіль користувача
                    user_profile.save()           
        
                # Перенаправляємо на вихідну сторінку
                return redirect(reverse('users', kwargs={'users_type': users_type}) + f'?show=student')
        else:
            form = RegistrationForm()
        context['form'] = form  # Додаємо форму в контекст, щоб передати її в шаблон
    return render(request, f'main/{users_type}.html', context)

@login_required
def account(request, user_type): # Функція свого профілю
    context = {
        'show_content': 'account',
        'full_name': request.user.full_name,
        'username': request.user.username,
        'email': request.user.email,
        'password': request.user.password,
        'user_type': request.user.user_type,
        'page_title': f"Ваш профіль {request.user.full_name}",
        'title': "Ваш профіль"
    }
    if request.user.is_block:
        context['is_block'] = 'Заблокований'
    elif not request.user.is_block:
        context['is_block'] = 'Розблокований'
    return render(request, f'main/{user_type}.html', context)

@login_required        
def materials(request, user_type): # Функція "Матеріали"
    videos = Video.objects.all()
    tests = Test.objects.all()
    context = {
        'show_content': 'materials',
        'page_title': 'Матеріали',
        'videos': videos,
        'tests': tests,
    }
    return render(request, f'main/{user_type}.html', context) 

@login_required
def take_test(request, user_type, test_id): # Функція "пройти тест"
    test = Test.objects.get(id=test_id)
    questions = test.questions.all()
    if request.method == 'POST':
        score = 0
        for question in questions:
            selected_answer = request.POST.get(f'question_{question.id}')
            correct_answer = question.answers.filter(is_correct=True).first()
            if correct_answer and str(correct_answer.id) == selected_answer:
                score += 1
        context = {
            'show_content': 'test_result',
            'page_title': f'Результат тесту "{test.title}"',
            'score': score,
            'total_questions': questions.count(),
        }
        return render(request, f'main/{user_type}.html', context)
    else:
        context = {
            'show_content': 'take_test',
            'page_title': f'Тест "{test.title}"',
            'test': test,
            'questions': questions,
        }
        return render(request, f'main/{user_type}.html', context)        

@login_required # Функція для списку відео        
def video_list(request, user_type):
    # Перевіряємо, чи є роль користувача дозволеною
    if user_type not in ['admin', 'teacher', 'moderator']:
        return HttpResponseForbidden()
    context = {
        'show_content': 'video_list',
        'page_title': 'Список відео',
        'videos': Video.objects.all()
    }
    return render(request, f'main/{user_type}.html', context)   

@login_required # Функція для додавання/редагування відео
def video_edit(request, user_type, video_id=None):
    # Перевіряємо, чи є роль користувача дозволеною
    if user_type not in ['admin', 'teacher', 'moderator']:
        return HttpResponseForbidden()
    context = {
        'show_content': 'video_edit',
        'page_title': 'Редагувати відео',
    }
    if video_id:
        video = get_object_or_404(Video, id=video_id)
    else:
        video = None
        context['page_title'] = 'Додати відео'
        
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            form.save()
            return redirect(reverse('video_list', kwargs={'user_type': user_type}))
    else:
        form = VideoForm(instance=video)
    context['form'] = form
    return render(request, f'main/{user_type}.html', context)    
    
@login_required # Функція для видалення відео
def video_delete(request, user_type, video_id):
    # Перевіряємо, чи є роль користувача дозволеною
    if user_type not in ['admin', 'teacher', 'moderator']:
        return HttpResponseForbidden()
    video = get_object_or_404(Video, id=video_id)
    if request.method == 'POST':
        # Отримуємо шлях до файлу відео
        video_file_path = video.video_file.path
        # Видаляємо запис із бази даних
        video.delete()
        # Видаляємо файл відео зі сховища
        default_storage.delete(video_file_path)
        return redirect(reverse('video_list', kwargs={'user_type': user_type}))
    context = {
        'show_content': 'video_delete',
        'page_title': 'Видалити відео',
        'video': video
    }
    return render(request, f'main/{user_type}.html', context)  

@login_required # Функція для списку тестів
def test_list(request, user_type):
    # Перевіряємо, чи є роль користувача дозволеною
    if user_type not in ['admin', 'teacher', 'moderator']:
        return HttpResponseForbidden()
    context = {
        'show_content': 'test_list',
        'page_title': 'Список тестів',
        'tests': Test.objects.all()
    }
    return render(request, f'main/{user_type}.html', context)

@login_required # Функція для додавання/редагування тесту
def test_edit(request, user_type, test_id=None):
    # Перевіряємо, чи є роль користувача дозволеною
    if user_type not in ['admin', 'teacher', 'moderator']:
        return HttpResponseForbidden()
    context = {
        'show_content': 'test_edit',
        'page_title': 'Редагувати тест',
    }
    if test_id:
        test = get_object_or_404(Test, id=test_id)
    else:
        test = None
        context['page_title'] = 'Додати тест'

    if request.method == 'POST':
        form = TestForm(request.POST, instance=test)
        if form.is_valid():
            test = form.save()
            return redirect(reverse('test_list', kwargs={'user_type': user_type}))
    else:
        form = TestForm(instance=test)
    context['test'] = test
    context['form'] = form
    return render(request, f'main/{user_type}.html', context)    

@login_required # Функція для видалення тесту
def test_delete(request, user_type, test_id):
    # Перевіряємо, чи є роль користувача дозволеною
    if user_type not in ['admin', 'teacher', 'moderator']:
        return HttpResponseForbidden()
    test = get_object_or_404(Test, id=test_id)
    if request.method == 'POST':
        # Видаляємо всі питання, пов'язані з тестом
        question = Question.objects.filter(test=test)
        question.delete()

        # Видаляємо сам тест
        test.delete()
        return redirect(reverse('test_list', kwargs={'user_type': user_type}))
    context = {
        'show_content': 'test_delete',
        'page_title': 'Видалити тест',
        'test': test
    }
    return render(request, f'main/{user_type}.html', context)    

@login_required # Функція для додавання запитання
def add_test_question(request, user_type, test_id):
    # Перевіряємо, чи є роль користувача дозволеною
    if user_type not in ['admin', 'teacher', 'moderator']:
        return HttpResponseForbidden()
    context = {
        'show_content': 'add_test_question',
        'page_title': 'Додати запитання',
    }
    test = get_object_or_404(Test, id=test_id)
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save()
            test.questions.add(question)
            return redirect(reverse('add_test_answers', kwargs={'user_type': user_type, 'test_id': test.id, 'question_id': question.id}))
    else:
        question_form = QuestionForm()
    context['test'] = test
    context['form'] = question_form
    return render(request, f'main/{user_type}.html', context)

@login_required # Функція для додавання відповідей
def add_test_answers(request, user_type, test_id, question_id):
    # Перевіряємо, чи є роль користувача дозволеною
    if user_type not in ['admin', 'teacher', 'moderator']:
        return HttpResponseForbidden()
    test = get_object_or_404(Test, id=test_id)
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            answer = answer_form.save(commit=False)
            answer.question = question
            answer.save()
            return redirect(reverse('add_test_answers', kwargs={'user_type': user_type, 'test_id': test.id, 'question_id': question.id}))
    else:
        answer_form = AnswerForm()
    context = {
        'show_content': 'add_test_answers',
        'page_title': 'Додати відповідь',
        'test': test,
        'form': answer_form,
        'question': question
    }
    return render(request, f'main/{user_type}.html', context)    
    
@login_required # Представление для видалення питання
def question_delete(request, user_type, test_id, question_id):
    # Перевіряємо, чи є роль користувача дозволеною
    if user_type not in ['admin', 'teacher', 'moderator']:
        return HttpResponseForbidden()
    test = get_object_or_404(Test, id=test_id)
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        # Видаляємо всі відповіді, пов'язані із запитанням
        answers = Answer.objects.filter(question=question)
        answers.delete()

        # Видаляємо саме питання
        question.delete()
        return redirect(reverse('test_edit', kwargs={'user_type': user_type, 'test_id': test.id}))
    context = {
        'show_content': 'question_delete',
        'page_title': 'Видалити питання',
        'question': question,
        'test': test,
    }
    return render(request, f'main/{user_type}.html', context)     