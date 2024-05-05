const editFullNameBtn = document.getElementById('edit_full_name');
const editLoginBtn = document.getElementById('edit_login');
const editEmailBtn = document.getElementById('edit_email');
const editPasswordBtn = document.getElementById('edit_password');
const saveChangesBtn = document.getElementById('save_changes');

const fullNameDisplay = document.getElementById('full_name_display');
const fullNameInput = document.getElementById('full_name_input');

const loginDisplay = document.getElementById('login_display');
const loginInput = document.getElementById('login_input');

const emailDisplay = document.getElementById('email_display');
const emailInput = document.getElementById('email_input');

const passwordDisplay = document.getElementById('password_display');
const passwordInput = document.getElementById('password_input');
const passwordInput2 = document.getElementById('password_input2');

editFullNameBtn.addEventListener('click', () => {
    fullNameDisplay.style.display = 'none';
    fullNameInput.style.display = 'inline';
    saveChangesBtn.style.display = 'inline';
});

editLoginBtn.addEventListener('click', () => {
    loginDisplay.style.display = 'none';
    loginInput.style.display = 'inline';
    saveChangesBtn.style.display = 'inline';
});

editEmailBtn.addEventListener('click', () => {
    emailDisplay.style.display = 'none';
    emailInput.style.display = 'inline';
    saveChangesBtn.style.display = 'inline';
});

editPasswordBtn.addEventListener('click', () => {
    passwordDisplay.style.display = 'none';
    passwordInput.style.display = 'inline';
	passwordInput2.style.display = 'inline';
    saveChangesBtn.style.display = 'inline';
});

// Обработка сохранения изменений
const csrfToken = Cookies.get('csrftoken');

function updateProfile(fullName, login, email, password, password2) {
    // Валідація полів
    const fullNameRegex = /^[A-Za-zА-Яа-яЁёІіЇїЄєҐґ\s]{16,40}$/;
    const loginRegex = /^[a-z0-9]{6,15}$/;
    const emailRegex = /^[a-zA-Z0-9._\%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    const passwordRegex = /^[a-zA-Z0-9]*$/;

    if (fullName!='' && !fullNameRegex.test(fullName)) {
        alert('ПІБ може містити тільки букви, довжиною від 16 до 40 символів.');
		return window.location.reload();
    }

    if (login!='' && !loginRegex.test(login)) {
        alert('Логін може містити тільки латинські літери та цифри, довжиною від 6 до 15 символів.');
        return window.location.reload();
    }

    if (email!='' && !emailRegex.test(email)) {
        alert('Введіть коректний email.');
		return window.location.reload();
    }

    if (password!='' && (!passwordRegex.test(password) || password.length < 6 || password.length > 15 || !/\d/.test(password) || !/[A-Z]/.test(password))) {
        alert('Пароль повинен містити тільки цифри і букви латинського алфавіту, мати довжину від 6 до 15 символів, містити хоча б одну цифру та одну велику літеру.');
		return window.location.reload();
    }
	
	if (password!=password2) {
        alert('Паролі не співпадають.');
		return window.location.reload();
    }

	const data = {
        full_name: fullName,
		login: login,
        email: email,
        password: password,
		old_login: loginDisplay.textContent
    };

    fetch('/update_profile/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
			if (password!='') {
				alert('Зміни збережені, але потрібно авторизуватись!');
			} else {
                alert('Зміни збережені');
			}
            window.location.reload();
        } else {
            const errorMessage = Object.values(data.error).join(', ');
            alert('Помилка при збереженні змін: ${errorMessage}');
			window.location.reload();
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Виникла помилка при збереженні даних');
		window.location.reload();
    });
}

saveChangesBtn.addEventListener('click', () => {
    const fullName = fullNameInput.value;
	const login = loginInput.value;
    const email = emailInput.value;
    const password = passwordInput.value;
	const password2 = passwordInput2.value;

    updateProfile(fullName, login, email, password, password2);
});