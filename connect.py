from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

print("1. Начало скрипта")

# Загрузка переменных окружения
load_dotenv()
print("2. Переменные окружения загружены")

# Проверим, что переменная есть
postgres_url = os.getenv("POSTGRES_URL")
print(f"3. POSTGRES_URL = {'***' if postgres_url else 'НЕ НАЙДЕН'}")

if not postgres_url:
    print("Ошибка: POSTGRES_URL не найден в .env файле")
    exit(1)

print("4. Создаем engine...")
engine = create_engine(postgres_url)

print("5. Пытаемся подключиться...")
try:
    with engine.connect() as conn:
        print("6. Подключение установлено")
        result = conn.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"7. Версия PostgreSQL: {version}")
except Exception as e:
    print(f"Ошибка подключения: {e}")
    
print("8. Конец скрипта")