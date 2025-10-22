document.addEventListener('DOMContentLoaded', function () {
    // Обработка изменения статуса задачи
    document.querySelectorAll('.task-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            const taskId = this.dataset.taskId;
            const status = this.checked ? 'completed' : 'in_progress';
            const taskItem = this.closest('.task-item');

            fetch('/update_task', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    task_id: taskId,
                    status: status
                })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        // Обновляем data-status элемента
                        taskItem.dataset.status = status;
                        // Применяем активный фильтр заново
                        const activeFilter = document.querySelector('.tasks .filter.active');
                        if (activeFilter) {
                            applyTaskFilter(activeFilter.dataset.filter);
                        }
                    } else {
                        this.checked = !this.checked; // возвращаем предыдущее состояние
                        alert('Ошибка при обновлении статуса задачи');
                    }
                });
        });
    });

    // Обработка изменения статуса привычки
    document.querySelectorAll('.habit-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            const habitId = this.dataset.habitId;
            const habitItem = this.closest('.habit-item');
            const currentStreak = parseInt(habitItem.querySelector('.habit-streak').textContent.match(/\d+/)[0]);
            const newStreak = this.checked ? currentStreak + 1 : Math.max(0, currentStreak - 1);

            fetch('/update_habit_streak', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    habit_id: habitId,
                    streak: newStreak
                })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        habitItem.querySelector('.habit-streak').textContent = `(Серия: ${newStreak})`;
                        // Обновляем data-status (активная привычка = streak > 0)
                        habitItem.dataset.status = newStreak > 0 ? 'completed' : 'in_progress';
                        // Применяем активный фильтр заново
                        const activeFilter = document.querySelector('.habits .filter.active');
                        if (activeFilter) {
                            applyHabitFilter(activeFilter.dataset.filter);
                        }
                    } else {
                        this.checked = !this.checked;
                        alert('Ошибка при обновлении привычки');
                    }
                });
        });
    });

    // Overlay и модальные
    const overlay = document.getElementById('modal-overlay');
    const modalTask = document.getElementById('modal-task');
    const modalHabit = document.getElementById('modal-habit');
    // Кнопки
    const addTaskBtn = document.querySelector('.tasks .icon-btn');
    const addHabitBtn = document.querySelector('.habits .icon-btn');
    const taskCreateBtn = document.getElementById('task-create-btn');
    const taskCancelBtn = document.getElementById('task-cancel-btn');
    const habitCreateBtn = document.getElementById('habit-create-btn');
    const habitCancelBtn = document.getElementById('habit-cancel-btn');

    // Открытие модалок
    if (addTaskBtn) {
        addTaskBtn.addEventListener('click', function () {
            overlay.style.display = 'block';
            modalTask.style.display = 'flex';
            document.getElementById('task-title').focus();
        });
    }

    if (addHabitBtn) {
        addHabitBtn.addEventListener('click', function () {
            overlay.style.display = 'block';
            modalHabit.style.display = 'flex';
            document.getElementById('habit-title').focus();
        });
    }
    // Закрытие модалок
    function closeModals() {
        overlay.style.display = 'none';
        modalTask.style.display = 'none';
        modalHabit.style.display = 'none';
        document.getElementById('task-title').value = '';
        document.getElementById('habit-title').value = '';
    }
    overlay.addEventListener('click', closeModals);
    if (taskCancelBtn) taskCancelBtn.onclick = closeModals;
    if (habitCancelBtn) habitCancelBtn.onclick = closeModals;
    // Создание задачи
    if (taskCreateBtn) taskCreateBtn.onclick = function () {
        const title = document.getElementById('task-title').value.trim();
        if (title) {
            fetch('/add_task', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) location.reload();
                    else alert('Ошибка при добавлении задачи');
                });
        }
        closeModals();
    };
    // Создание привычки
    if (habitCreateBtn) habitCreateBtn.onclick = function () {
        const title = document.getElementById('habit-title').value.trim();
        if (title) {
            fetch('/add_habit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) location.reload();
                    else alert('Ошибка при добавлении привычки');
                });
        }
        closeModals();
    };

    //Фильтры

    // Функция фильтрации задач
    function applyTaskFilter(filter) {
        const taskItems = document.querySelectorAll('.tasks .task-item');
        taskItems.forEach(item => {
            if (filter === 'active') {
                item.style.display = item.dataset.status === 'in_progress' ? '' : 'none';
            } else if (filter === 'completed') {
                item.style.display = item.dataset.status === 'completed' ? '' : 'none';
            }
        });
    }

    // Функция фильтрации привычек
    function applyHabitFilter(filter) {
        const habitItems = document.querySelectorAll('.habits .habit-item');
        habitItems.forEach(item => {
            if (filter === 'all') {
                item.style.display = '';
            } else if (filter === 'active') {
                item.style.display = item.dataset.status === 'in_progress' ? '' : 'none';
            } else if (filter === 'completed') {
                item.style.display = item.dataset.status === 'completed' ? '' : 'none';
            }
        });
    }

    // Обработчики кликов на фильтры задач
    document.querySelectorAll('.tasks .filter').forEach(item => {
        item.addEventListener('click', function () {
            document.querySelectorAll('.tasks .filter').forEach(el => el.classList.remove('active'));
            this.classList.add('active');
            applyTaskFilter(this.dataset.filter);
        });
    });

    // Обработчики кликов на фильтры привычек
    document.querySelectorAll('.habits .filter').forEach(item => {
        item.addEventListener('click', function () {
            document.querySelectorAll('.habits .filter').forEach(el => el.classList.remove('active'));
            this.classList.add('active');
            applyHabitFilter(this.dataset.filter);
        });
    });

    // По умолчанию применяем фильтр "Активные" для задач и привычек
    applyTaskFilter('active');
    applyHabitFilter('active');
});
