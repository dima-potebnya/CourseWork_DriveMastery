document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('logout-link').addEventListener('click', function(event) {
        event.preventDefault(); // Отменяем стандартное действие ссылки
        
        // Выводим диалоговое окно с подтверждением
        var confirmation = confirm('Ви дійсно хочете вийти?');
        
        // Если пользователь подтвердил выход, перенаправляем его на /logout/
        if (confirmation) {
            window.location.href = '/logout/'; // Перенаправляем пользователя на URL-адрес для выхода
        }
    });
});