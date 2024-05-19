import secrets

# Генеруємо секретний код довжиною 32 символи
secret_admin_code = secrets.token_urlsafe(32)
print(secret_admin_code)