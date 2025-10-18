from flask import render_template, request, jsonify
from app import app

# Временные данные для демонстрации
user_data = {
    'nickname': 'Пользователь',
    'avatar': 'default_avatar.png',
    'rating': 100,
    'achievements': [
        {'title': 'Первые шаги', 'description': 'Создание аккаунта'},
        {'title': 'На старте', 'description': 'Первая выполненная задача'}
    ],
    'tasks': [
        {'title': 'Изучить Flask', 'status': 'в процессе'},
        {'title': 'Создать профиль', 'status': 'выполнено'}
    ],
    'habits': [
        {'title': 'Ежедневное чтение', 'streak': 5},
        {'title': 'Утренняя зарядка', 'streak': 3}
    ]
}

@app.route('/')
def index():
    """Главная страница с профилем пользователя"""
    return render_template('index.html', user=user_data)

@app.route('/update_rating', methods=['POST'])
def update_rating():
    """Обновление рейтинга пользователя"""
    if request.method == 'POST':
        new_rating = request.json.get('rating')
        if new_rating is not None:
            user_data['rating'] = new_rating
            return jsonify({'success': True, 'new_rating': new_rating})
    return jsonify({'success': False}), 400

@app.route('/add_achievement', methods=['POST'])
def add_achievement():
    """Добавление нового достижения"""
    if request.method == 'POST':
        title = request.json.get('title')
        description = request.json.get('description')
        if title and description:
            user_data['achievements'].append({
                'title': title,
                'description': description
            })
            return jsonify({'success': True})
    return jsonify({'success': False}), 400

@app.route('/add_task', methods=['POST'])
def add_task():
    """Добавление новой задачи"""
    if request.method == 'POST':
        title = request.json.get('title')
        if title:
            user_data['tasks'].append({
                'title': title,
                'status': 'в процессе'
            })
            return jsonify({'success': True})
    return jsonify({'success': False}), 400

@app.route('/update_task', methods=['POST'])
def update_task():
    """Обновление статуса задачи"""
    if request.method == 'POST':
        title = request.json.get('title')
        status = request.json.get('status')
        if title and status:
            for task in user_data['tasks']:
                if task['title'] == title:
                    task['status'] = status
                    return jsonify({'success': True})
    return jsonify({'success': False}), 400

@app.route('/add_habit', methods=['POST'])
def add_habit():
    """Добавление новой привычки"""
    if request.method == 'POST':
        title = request.json.get('title')
        if title:
            user_data['habits'].append({
                'title': title,
                'streak': 0
            })
            return jsonify({'success': True})
    return jsonify({'success': False}), 400

@app.route('/update_habit_streak', methods=['POST'])
def update_habit_streak():
    """Обновление счетчика привычки"""
    if request.method == 'POST':
        title = request.json.get('title')
        new_streak = request.json.get('streak')
        if title and new_streak is not None:
            for habit in user_data['habits']:
                if habit['title'] == title:
                    habit['streak'] = new_streak
                    return jsonify({'success': True})
    return jsonify({'success': False}), 400

@app.route('/update_profile', methods=['POST'])
def update_profile():
    """Обновление профиля пользователя"""
    if request.method == 'POST':
        nickname = request.json.get('nickname')
        if nickname:
            user_data['nickname'] = nickname
            return jsonify({'success': True})
    return jsonify({'success': False}), 400
