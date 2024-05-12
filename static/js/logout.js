// Функція виходу (деаутентифікації)
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('logout-link').addEventListener('click', function(event) {
        event.preventDefault(); // Скасовуємо стандартну дію посилання
        
        // Виводимо діалогове вікно з підтвердженням
        var confirmation = confirm('Ви дійсно хочете вийти?');
        
        // Якщо користувач підтвердив вихід, перенаправляємо його на /logout/
        if (confirmation) {
            window.location.href = '/logout/'; // Перенаправляємо користувача на URL-адресу для виходу
        }
    });
});