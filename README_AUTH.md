# Инструкция по использованию системы аутентификации

## Что было изменено

### 1. **database/models.py**
- Удалены методы `set_password()` и `check_password()` из модели `User`
- Добавлены обратные связи (relationships) для всех моделей
- Переименован `Stats` → `UserStats`, `Habits` → `Habit`

### 2. **database/database.py**
- Добавлены полноценные методы для работы с БД:
  - **User**: `add_user()`, `get_user_by_id()`, `get_user_by_username()`, `get_user_by_email()`, `verify_user_password()`
  - **Stats**: `get_user_stats()`, `update_user_rating()`, `add_user_rating()`
  - **Tasks**: `add_user_task()`, `get_user_tasks()`, `update_task_status()`, `delete_task()`
  - **Habits**: `add_user_habit()`, `get_user_habits()`, `update_habit_streak()`, `delete_habit()`
  - **Achievements**: `add_user_achievement()`, `get_user_achievements()`
- Используется `auth.py` для хеширования паролей через bcrypt

### 3. **app/views/routes.py**
- Все маршруты теперь используют методы из `database.py` вместо прямых SQL-запросов
- Обновлены endpoints для работы с `task_id` и `habit_id` вместо `title`

### 4. **app/templates/index.html**
- Добавлены `data-task-id` и `data-habit-id` атрибуты к чекбоксам
- Исправлен синтаксис Jinja для привычек
- Статус задач изменён с русских значений на `in_progress` / `completed`

### 5. **app/static/js/script.js**
- Обновлены обработчики для использования ID вместо названий
- Статусы задач теперь `completed` / `in_progress`

## Установка зависимостей

```cmd
pip install flask flask-login bcrypt python-dotenv sqlalchemy psycopg2-binary
```

## Настройка

1. **Создайте файл `.env` в корне проекта**:
```
DB_URL=postgresql://username:password@localhost:5432/database_name
SECRET_KEY=your-secret-key-here
```

2. **Создайте таблицы в БД**:
```python
from database.database import db
db.create_tables()
```

## Использование

### Регистрация пользователя
```python
from database.database import db

# Создание пользователя
user = db.add_user(
    nickname="Иван",
    username="ivan123",
    email="ivan@example.com",
    password="securepassword123"
)
```

### Проверка пароля
```python
user = db.get_user_by_username("ivan123")
is_valid = db.verify_user_password(user, "securepassword123")
```

### Работа с задачами
```python
# Добавить задачу
task = db.add_user_task(user.id, "Изучить Python")

# Получить все задачи
tasks = db.get_user_tasks(user.id)

# Получить только выполненные задачи
completed_tasks = db.get_user_tasks(user.id, status='completed')

# Обновить статус
db.update_task_status(task.id, 'completed')
```

### Работа с привычками
```python
# Добавить привычку
habit = db.add_user_habit(user.id, "Утренняя зарядка")

# Получить привычки
habits = db.get_user_habits(user.id)

# Обновить серию
db.update_habit_streak(habit.id, 5)
```

### Работа со статистикой
```python
# Получить статистику
stats = db.get_user_stats(user.id)

# Установить рейтинг
db.update_user_rating(user.id, 1000)

# Добавить к рейтингу
db.add_user_rating(user.id, 50)  # +50 к текущему рейтингу
```

## Запуск приложения

```cmd
flask run
```

Или через `run.py`:
```cmd
python run.py
```

## Структура проекта

```
RatingHabits/
├── app/
│   ├── __init__.py          # Flask app + Flask-Login
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── script.js    # Обновлён для работы с ID
│   ├── templates/
│   │   ├── index.html       # Главная страница (требует авторизации)
│   │   ├── login.html       # Страница входа
│   │   └── register.html    # Страница регистрации
│   └── views/
│       └── routes.py        # Маршруты с использованием database.py
├── database/
│   ├── database.py          # Класс Database с методами работы с БД
│   └── models.py            # SQLAlchemy модели
├── auth.py                  # Функции bcrypt для паролей
├── run.py                   # Точка входа
└── .env                     # Конфигурация (создать вручную)
```

## Важные изменения в коде

### Было (старый подход):
```python
# В routes.py
user.set_password(password)
user.check_password(password)

# В script.js
data-task-title="{{ task.title }}"
```

### Стало (новый подход):
```python
# В routes.py
db.add_user(..., password=password)  # Хеширование внутри
db.verify_user_password(user, password)

# В script.js
data-task-id="{{ task.id }}"
```

## Примечания

- Все пароли хешируются через bcrypt в `auth.py`
- Все страницы кроме `/login` и `/register` требуют авторизации
- При регистрации автоматически создаётся запись в `UserStats`
- ID передаются в JavaScript для более надёжной работы с БД
