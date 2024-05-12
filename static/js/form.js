// Функція для відображення додаткового поля з секретним кодом для адмінів
document.addEventListener("DOMContentLoaded", function() { 
    var roleField = document.getElementById("id_role");
    var categoryField = document.getElementById("id_secret_admin_code");

    function toggleCategoryField() {
        if (roleField.value === "admin") {
            categoryField.parentElement.style.display = "block";
        } else {
            categoryField.parentElement.style.display = "none";
        }
    }

    roleField.addEventListener("change", toggleCategoryField);
    toggleCategoryField();  // Вызываем функцию один раз при загрузке страницы
});
// Функція для перенаправлення на сторінку авторизації
function redirectToLogin() {
    window.location.href = "/guest_main/login/";
}
// Функція для перенаправлення на сторінку реєстрації
function redirectToRegister() {
    window.location.href = "/guest_main/register/";
}		