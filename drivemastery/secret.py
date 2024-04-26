import secrets

# Генерируем секретный код длиной 32 символа
secret_admin_code = secrets.token_urlsafe(32)
print(secret_admin_code)