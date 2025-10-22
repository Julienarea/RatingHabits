from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import app, login_manager
from app.utils.paths import avatar_url
from database.models import User
from database.database import db

# User loader для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.get_user_by_id(int(user_id))

# Маршруты аутентификации
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Поиск пользователя по username или email
        user = db.get_user_by_username(username)
        if not user:
            user = db.get_user_by_email(username)
        
        if user and db.verify_user_password(user, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('index'))
        else:
            return render_template('login.html', error='Неверное имя пользователя или пароль')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        nickname = request.form.get('nickname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Валидация username: только латиница, цифры, без пробелов
        import re
        if not re.match(r'^[A-Za-z0-9\-_]+$', username):
            return render_template('register.html', error='Имя пользователя должно содержать только латинские буквы и цифры, без пробелов')

        if password != confirm_password:
            return render_template('register.html', error='Пароли не совпадают')

        # Проверка существующих пользователей
        if db.get_user_by_username(username):
            return render_template('register.html', error='Имя пользователя уже занято')
        if db.get_user_by_email(email):
            return render_template('register.html', error='Email уже зарегистрирован')
        
        try:
            # Создание нового пользователя
            new_user = db.add_user(
                nickname=nickname,
                username=username,
                email=email,
                password=password
            )
            
            # Автоматический вход после регистрации
            login_user(new_user)
            return redirect(url_for('index'))
        except Exception as e:
            return render_template('register.html', error=f'Ошибка при регистрации: {str(e)}')
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """Выход из системы"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Главная страница с профилем пользователя"""
    # Получаем данные пользователя из БД
    user_stats = db.get_user_stats(current_user.id)
    user_tasks = db.get_user_tasks(current_user.id)
    user_habits = db.get_user_habits(current_user.id)
    user_achievements = db.get_user_achievements(current_user.id)
    
    # path_to_avatar теперь трактуем как «имя файла» (filename), а полный URL строим через helper
    user_data = {
        'nickname': current_user.nickname,
        'username': current_user.username,
        'avatar': avatar_url(current_user.path_to_avatar),  # возвращает полный URL к static
        'rating': user_stats.rating if user_stats else 0,
        'achievements': [
            {'title': ach.title, 'description': ach.description}
            for ach in user_achievements
        ],
        'tasks': [
            {'id': task.id, 'title': task.title, 'status': task.status}
            for task in user_tasks
        ],
        'habits': [
            {'id': habit.id, 'title': habit.title, 'streak': habit.streak}
            for habit in user_habits
        ]
    }
    return render_template('index.html', user=user_data)

@app.route('/update_rating', methods=['POST'])
@login_required
def update_rating():
    """Обновление рейтинга пользователя"""
    if request.method == 'POST':
        new_rating = request.json.get('rating')
        if new_rating is not None:
            try:
                db.update_user_rating(current_user.id, new_rating)
                return jsonify({'success': True, 'new_rating': new_rating})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 400
    return jsonify({'success': False}), 400

@app.route('/add_achievement', methods=['POST'])
@login_required
def add_achievement():
    """Добавление нового достижения"""
    if request.method == 'POST':
        title = request.json.get('title')
        description = request.json.get('description')
        if title and description:
            try:
                db.add_user_achievement(current_user.id, title, description)
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 400
    return jsonify({'success': False}), 400

@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    """Добавление новой задачи"""
    if request.method == 'POST':
        title = request.json.get('title')
        if title:
            try:
                db.add_user_task(current_user.id, title)
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 400
    return jsonify({'success': False}), 400

@app.route('/update_task', methods=['POST'])
@login_required
def update_task():
    """Обновление статуса задачи"""
    if request.method == 'POST':
        task_id = request.json.get('task_id')
        status = request.json.get('status')
        if task_id and status:
            try:
                db.update_task_status(task_id, status)
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 400
    return jsonify({'success': False}), 400

@app.route('/add_habit', methods=['POST'])
@login_required
def add_habit():
    """Добавление новой привычки"""
    if request.method == 'POST':
        title = request.json.get('title')
        if title:
            try:
                db.add_user_habit(current_user.id, title)
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 400
    return jsonify({'success': False}), 400

@app.route('/update_habit_streak', methods=['POST'])
@login_required
def update_habit_streak():
    """Обновление счетчика привычки"""
    if request.method == 'POST':
        habit_id = request.json.get('habit_id')
        new_streak = request.json.get('streak')
        if habit_id and new_streak is not None:
            try:
                db.update_habit_streak(habit_id, new_streak)
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 400
    return jsonify({'success': False}), 400

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    """Обновление профиля пользователя"""
    if request.method == 'POST':
        nickname = request.json.get('nickname')
        if nickname:
            # TODO: Добавить метод update_user_profile в database.py
            return jsonify({'success': True})
    return jsonify({'success': False}), 400
