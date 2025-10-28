from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import app, login_manager
from app.utils.paths import avatar_url
from database.models import User
from database.database import db
from functions import is_habit_active
import sys
import pytz
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
# ...existing code...

# === Вставляем роут после импортов и до остальных маршрутов ===
@app.route('/get_habit_details')
@login_required
def get_habit_details():
    habit_id = request.args.get('habit_id')
    if not habit_id:
        return jsonify({'success': False, 'error': 'No habit_id'}), 400
    user_habits = db.get_user_habits(current_user.id)
    habit = next((h for h in user_habits if str(h.id) == str(habit_id)), None)
    if not habit:
        return jsonify({'success': False, 'error': 'Not found'}), 404
    return jsonify({
        'success': True,
        'habit': {
            'id': habit.id,
            'title': habit.title,
            'notes': habit.notes,
            'difficulty': habit.difficulty,
            'streak': habit.streak,
            'start_date': habit.start_date,
            'repeat_type': habit.repeat_type,
            'repeat_every': habit.repeat_every,
            'repeat_days': habit.repeat_days
        }
    })
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
        
        # Валидация username: только латиница, цифры, дефис, подчёркивание
        import re
        if not re.match(r'^[A-Za-z0-9_-]+$', username):
            return render_template('register.html', error='Имя пользователя должно содержать только латинские буквы, цифры, дефис и подчёркивание')

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
    tz = pytz.timezone('Asia/Yekaterinburg')
    today = datetime.now(tz).date()
    yesterday = today - timedelta(days=1)

    user_stats = db.get_user_stats(current_user.id)
    user_tasks = db.get_user_tasks(current_user.id)
    user_habits = db.get_user_habits(current_user.id)
    user_achievements = db.get_user_achievements(current_user.id)

    # === 1. Проверка пропусков ЗА ВЧЕРА (пока completed_today ещё за вчера) ===
    for habit in user_habits:
        # Пропускаем, если привычка ещё не началась
        start_date = None
        if habit.start_date:
            try:
                start_date = datetime.strptime(habit.start_date, '%Y-%m-%d').date()
                if today < start_date:
                    continue
            except:
                pass
        if start_date is None:
            start_date = today

        # Не штрафуем за пропуск, если привычка только что создана (её start_date >= yesterday)
        if start_date > yesterday:
            db.update_habit_last_checked(habit.id, yesterday.strftime('%Y-%m-%d'))
            continue

        # Проверяем ТОЛЬКО вчерашний день (упрощаем логику)
        if is_habit_active(habit, yesterday):
            # Если не была выполнена к концу вчерашнего дня
            if not habit.completed_today:  # ← это состояние на конец дня
                points_table = {
                    'trivial': (10, -30),
                    'easy': (25, -25),
                    'medium': (40, -20),
                    'hard': (60, -15),
                }
                pts = points_table.get(habit.difficulty, (25, -25))
                db.add_user_rating(current_user.id, pts[1])
                db.update_habit_streak(habit.id, 0)

        # Обновляем last_checked_date до вчера
        db.update_habit_last_checked(habit.id, yesterday.strftime('%Y-%m-%d'))

    # === 2. Сброс completed_today для СЕГОДНЯ ===
    for habit in user_habits:
        if is_habit_active(habit, today):
            db.update_habit_completed_today(habit.id, False)

    # === 3. Обновляем данные после изменений ===
    user_stats = db.get_user_stats(current_user.id)
    user_habits = db.get_user_habits(current_user.id)

    # === 4. Формируем данные для шаблона ===
    user_data = {
        'nickname': current_user.nickname,
        'username': current_user.username,
        'avatar': avatar_url(current_user.path_to_avatar),
        'rating': user_stats.rating if user_stats else 0,
        'achievements': [
            {'title': ach.title, 'description': ach.description}
            for ach in user_achievements
        ],
        'tasks': [
            {
                'id': task.id,
                'title': task.title,
                'status': task.status,
                'notes': task.notes,
                'difficulty': task.difficulty,
                'deadline': task.deadline.strftime('%Y-%m-%d') if task.deadline else None
            }
            for task in user_tasks
        ],
        'habits': [
            {
                'id': habit.id,
                'title': habit.title,
                'streak': habit.streak,
                'difficulty': habit.difficulty,
                'notes': habit.notes,
                'active': is_habit_active(habit, today)
            }
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
        notes = request.json.get('notes')
        difficulty = request.json.get('difficulty', 'easy')
        deadline = request.json.get('deadline')
        if deadline == '':
            deadline = None
        if title:
            try:
                db.add_user_task(
                    user_id=current_user.id,
                    title=title,
                    notes=notes,
                    difficulty=difficulty,
                    deadline=deadline
                )
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
        difficulty = request.json.get('difficulty', 'easy')
        # Таблица баллов: 1-trivial, 2-easy, 3-medium, 4-hard
        # 1: +10/-30, 2: +25/-25, 3: +40/-20, 4: +60/-15
        points_table = {
            'trivial': (10, -30),
            'easy': (25, -25),
            'medium': (40, -20),
            'hard': (60, -15),
        }
        if task_id and status:
            try:
                db.update_task_status(task_id, status)
                # Изменение рейтинга
                pts = points_table.get(difficulty, (10, -30))
                delta = pts[0] if status == 'completed' else pts[1]
                db.add_user_rating(current_user.id, delta)
                return jsonify({'success': True, 'rating_delta': delta})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 400
    return jsonify({'success': False}), 400

@app.route('/update_task_details', methods=['POST'])
@login_required
def update_task_details():
    """Обновление полной информации о задаче (все поля)"""
    if request.method == 'POST':
        task_id = request.json.get('task_id')
        title = request.json.get('title')
        notes = request.json.get('notes')
        difficulty = request.json.get('difficulty')
        deadline = request.json.get('deadline')
        # Можно добавить другие поля, если появятся
        if task_id and title:
            try:
                db.update_task_details(
                    task_id=task_id,
                    title=title,
                    notes=notes,
                    difficulty=difficulty,
                    deadline=deadline
                )
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 400
    return jsonify({'success': False}), 400

@app.route('/delete_task', methods=['POST'])
@login_required
def delete_task_route():
    """Удаление задачи"""
    if request.method == 'POST':
        task_id = request.json.get('task_id')
        if task_id:
            try:
                db.delete_task(task_id)
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
        notes = request.json.get('notes')
        difficulty = request.json.get('difficulty', 'easy')
        start_date = request.json.get('start_date')
        repeat_type = request.json.get('repeat_type', 'weekly')
        repeat_every = request.json.get('repeat_every', 1)
        repeat_days = request.json.get('repeat_days', '1,2,3,4,5')
        
        if title:
            try:
                db.add_user_habit(
                    user_id=current_user.id,
                    title=title,
                    notes=notes,
                    difficulty=difficulty,
                    start_date=start_date,
                    repeat_type=repeat_type,
                    repeat_every=repeat_every,
                    repeat_days=repeat_days
                )
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 400
    return jsonify({'success': False}), 400

@app.route('/update_habit_details', methods=['POST'])
@login_required
def update_habit_details():
    """Обновление всех полей привычки (title, notes, difficulty, start_date, repeat_type, repeat_every, repeat_days, streak)"""
    
    if request.method == 'POST':
        data = request.json
        print('DEBUG /update_habit_details data:', data, file=sys.stderr)
        habit_id = data.get('habit_id')
        title = data.get('title')
        notes = data.get('notes')
        difficulty = data.get('difficulty')
        start_date = data.get('start_date')
        repeat_type = data.get('repeat_type')
        repeat_every = data.get('repeat_every')
        repeat_days = data.get('repeat_days')
        streak = data.get('streak')
        if habit_id and title:
            try:
                db.update_habit_details(
                    habit_id=habit_id,
                    title=title,
                    notes=notes,
                    difficulty=difficulty,
                    start_date=start_date,
                    repeat_type=repeat_type,
                    repeat_every=repeat_every,
                    repeat_days=repeat_days,
                    streak=streak
                )
                return jsonify({'success': True})
            except Exception as e:
                print('ERROR /update_habit_details:', str(e), file=sys.stderr)
                return jsonify({'success': False, 'error': str(e)}), 400
        else:
            print('ERROR /update_habit_details: habit_id or title missing', file=sys.stderr)
        return jsonify({'success': False}), 400

@app.route('/delete_habit', methods=['POST'])
@login_required
def delete_habit_route():
    """Удаление привычки"""
    if request.method == 'POST':
        habit_id = request.json.get('habit_id')
        if habit_id:
            try:
                db.delete_habit(habit_id)
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 400
    return jsonify({'success': False}), 400

@app.route('/update_habit_streak', methods=['POST'])
@login_required
def update_habit_streak():
    data = request.json
    print("🔍 RAW DATA:", request.get_data(as_text=True), file=sys.stderr)
    print("🔍 PARSED JSON:", request.json, file=sys.stderr)
    habit_id = data.get('habit_id')
    completed = data.get('completed')
    difficulty = data.get('difficulty', 'easy')

    if habit_id is None or completed is None:
        print('ERROR: missing habit_id or completed', file=sys.stderr)
        return jsonify({'success': False, 'error': 'Missing habit_id or completed'}), 400

    try:
        habit = db.get_habit_by_id(habit_id)
        if not habit:
            return jsonify({'success': False, 'error': 'Habit not found'}), 404

        points_table = {
            'trivial': (10, -30),
            'easy': (25, -25),
            'medium': (40, -20),
            'hard': (60, -15),
        }
        pts = points_table.get(difficulty, (25, -25))

        if completed:
            # Выполнил: отмечаем как выполненную, +баллы, +стрик
            db.update_habit_completed_today(habit_id, True)
            db.update_habit_streak(habit_id, habit.streak + 1)
            db.add_user_rating(current_user.id, pts[0])
            delta = pts[0]
        else:
            # Отменил: сбрасываем выполнение, –баллы, –стрик
            db.update_habit_completed_today(habit_id, False) 
            new_streak = max(0, habit.streak - 1)
            db.update_habit_streak(habit_id, new_streak)
            db.add_user_rating(current_user.id, -pts[0])
            delta = -pts[0]

        return jsonify({'success': True, 'rating_delta': delta})

    except Exception as e:
        print('ERROR /update_habit_streak:', str(e), file=sys.stderr)
        return jsonify({'success': False, 'error': str(e)}), 400

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
