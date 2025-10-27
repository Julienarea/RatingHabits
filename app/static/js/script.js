document.addEventListener('DOMContentLoaded', function () {
    // Обработка изменения статуса задачи
    document.querySelectorAll('.task-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            const taskId = this.dataset.taskId;
            const status = this.checked ? 'completed' : 'in_progress';
            const taskItem = this.closest('.task-item');
            // Получаем сложность задачи из DOM
            let difficulty = 'easy';
            const diffEl = taskItem.querySelector('[class*="task-difficulty-"]');
            if (diffEl) {
                const match = diffEl.className.match(/task-difficulty-([a-z]+)/);
                if (match) difficulty = match[1];
            }
            fetch('/update_task', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    task_id: taskId,
                    status: status,
                    difficulty: difficulty
                })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        // Обновляем data-status элемента
                        taskItem.dataset.status = status;
                        // Обновляем рейтинг на странице
                        const ratingEl = document.querySelector('.profile-rating-value');
                        if (ratingEl && typeof data.rating_delta === 'number') {
                            let current = parseInt(ratingEl.textContent) || 0;
                            current += data.rating_delta;
                            ratingEl.textContent = current;
                        }
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

            const streakBadge = habitItem.querySelector('.habit-streak-badge');
            const currentStreak = streakBadge ? parseInt(streakBadge.textContent.match(/\d+/)[0]) : 0;
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
                        if (streakBadge) streakBadge.textContent = `🔥 Серия: ${newStreak}`;
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
    const modalTaskEdit = document.getElementById('modal-task-edit');
    const modalHabitEdit = document.getElementById('modal-habit-edit');

    // Кнопки
    const addTaskBtn = document.querySelector('.tasks .icon-btn');
    const addHabitBtn = document.querySelector('.habits .icon-btn');
    const taskCreateBtn = document.getElementById('task-create-btn');
    const taskCancelBtn = document.getElementById('task-cancel-btn');
    const habitCreateBtn = document.getElementById('habit-create-btn');
    const habitCancelBtn = document.getElementById('habit-cancel-btn');

    const taskEditSaveBtn = document.getElementById('task-edit-save-btn');
    const taskEditCancelBtn = document.getElementById('task-edit-cancel-btn');
    const taskDeleteBtn = document.getElementById('task-delete-btn');

    const habitEditSaveBtn = document.getElementById('habit-edit-save-btn');
    const habitEditCancelBtn = document.getElementById('habit-edit-cancel-btn');
    const habitDeleteBtn = document.getElementById('habit-delete-btn');

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
        modalTaskEdit.style.display = 'none';
        modalHabitEdit.style.display = 'none';
        document.getElementById('task-title').value = '';
        document.getElementById('task-notes').value = '';
        document.getElementById('task-difficulty').value = 'easy';
        document.getElementById('task-deadline').value = '';
        document.getElementById('habit-title').value = '';
        document.getElementById('habit-notes').value = '';
    }
    overlay.addEventListener('click', closeModals);
    if (taskCancelBtn) taskCancelBtn.onclick = closeModals;
    if (habitCancelBtn) habitCancelBtn.onclick = closeModals;
    if (taskEditCancelBtn) taskEditCancelBtn.onclick = closeModals;
    if (habitEditCancelBtn) habitEditCancelBtn.onclick = closeModals;

    // Открыть модальное окно редактирования задачи
    document.querySelectorAll('.task-content').forEach(taskContent => {
        taskContent.addEventListener('click', function (e) {
            const taskItem = this.closest('.task-item');
            const taskId = taskItem.dataset.taskId;

            // Получаем данные задачи из DOM
            const title = taskItem.querySelector('.task-title').textContent;
            const notesEl = taskItem.querySelector('.task-notes');
            const notes = notesEl ? notesEl.textContent : '';
            const difficultyEl = taskItem.querySelector('[class*="task-difficulty-"]');
            const difficulty = difficultyEl ? difficultyEl.className.split('task-difficulty-')[1].split(' ')[0] : 'easy';
            const deadlineEl = taskItem.querySelector('.task-deadline');
            const deadline = deadlineEl ? deadlineEl.textContent.replace('📅 ', '') : '';

            // Заполняем форму редактирования
            document.getElementById('task-edit-id').value = taskId;
            document.getElementById('task-edit-title').value = title;
            document.getElementById('task-edit-notes').value = notes;
            document.getElementById('task-edit-difficulty').value = difficulty;
            document.getElementById('task-edit-deadline').value = deadline;

            // Показываем модальное окно
            overlay.style.display = 'block';
            modalTaskEdit.style.display = 'flex';
        });
    });
    overlay.addEventListener('click', closeModals);
    if (taskCancelBtn) taskCancelBtn.onclick = closeModals;
    if (habitCancelBtn) habitCancelBtn.onclick = closeModals;

    // Создание задачи
    if (taskCreateBtn) taskCreateBtn.onclick = function () {
        const title = document.getElementById('task-title').value.trim();
        const notes = document.getElementById('task-notes').value.trim();
        const difficulty = document.getElementById('task-difficulty').value;
        const deadline = document.getElementById('task-deadline').value;

        if (title) {
            fetch('/add_task', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: title,
                    notes: notes,
                    difficulty: difficulty,
                    deadline: deadline
                })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) location.reload();
                    else alert('Ошибка при добавлении задачи');
                });
        }
        closeModals();
    };

    // Сохранение изменений задачи
    if (taskEditSaveBtn) taskEditSaveBtn.onclick = function () {
        const taskId = document.getElementById('task-edit-id').value;
        const title = document.getElementById('task-edit-title').value.trim();
        const notes = document.getElementById('task-edit-notes').value.trim();
        const difficulty = document.getElementById('task-edit-difficulty').value;
        const deadline = document.getElementById('task-edit-deadline').value;

        if (title && taskId) {
            fetch('/update_task_details', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    task_id: taskId,
                    title: title,
                    notes: notes,
                    difficulty: difficulty,
                    deadline: deadline
                })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) location.reload();
                    else alert('Ошибка при обновлении задачи');
                });
        }
        closeModals();
    };

    // Удаление задачи
    if (taskDeleteBtn) taskDeleteBtn.onclick = function () {
        const taskId = document.getElementById('task-edit-id').value;

        if (confirm('Вы уверены, что хотите удалить эту задачу?') && taskId) {
            fetch('/delete_task', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task_id: taskId })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) location.reload();
                    else alert('Ошибка при удалении задачи');
                });
        }
    };

    // Открыть модальное окно редактирования привычки
    document.querySelectorAll('.habit-content').forEach(habitContent => {
        habitContent.addEventListener('click', function (e) {
            const habitItem = this.closest('.habit-item');
            const habitId = habitItem.dataset.habitId;

            // Получаем данные привычки из БД через AJAX
            fetch(`/get_habit_details?habit_id=${habitId}`)
                .then(res => res.json())
                .then(data => {
                    if (data.success && data.habit) {
                        document.getElementById('habit-edit-id').value = data.habit.id;
                        document.getElementById('habit-edit-title').value = data.habit.title || '';
                        document.getElementById('habit-edit-notes').value = data.habit.notes || '';
                        document.getElementById('habit-edit-difficulty').value = data.habit.difficulty || 'easy';
                        document.getElementById('habit-edit-start-date').value = data.habit.start_date || '';
                        document.getElementById('habit-edit-repeat-type').value = data.habit.repeat_type || 'weekly';
                        document.getElementById('habit-edit-repeat-every').value = data.habit.repeat_every || 1;
                        // Сбросить все дни недели
                        document.querySelectorAll('#modal-habit-edit .day-toggle').forEach(btn => btn.classList.remove('active'));
                        if (data.habit.repeat_days) {
                            const daysArr = data.habit.repeat_days.split(',').map(d => d.trim());
                            document.querySelectorAll('#modal-habit-edit .day-toggle').forEach(btn => {
                                if (daysArr.includes(btn.dataset.day)) btn.classList.add('active');
                            });
                        }
                        // Обновить подпись периода
                        const repeatTypeSelect = document.getElementById('habit-edit-repeat-type');
                        const repeatLabel = document.getElementById('habit-edit-repeat-label');
                        if (repeatTypeSelect && repeatLabel) {
                            const labels = {
                                'daily': 'день',
                                'weekly': 'неделю',
                                'monthly': 'месяц',
                                'yearly': 'год'
                            };
                            repeatLabel.textContent = labels[repeatTypeSelect.value] || 'неделю';
                        }
                        overlay.style.display = 'block';
                        modalHabitEdit.style.display = 'flex';
                    } else {
                        alert('Ошибка загрузки данных привычки');
                    }
                });
        });
    });

    // Сохранение изменений привычки
    if (habitEditSaveBtn) habitEditSaveBtn.onclick = function () {
        const habitId = document.getElementById('habit-edit-id').value;
        const title = document.getElementById('habit-edit-title').value.trim();
        const notes = document.getElementById('habit-edit-notes').value.trim();
        const difficulty = document.getElementById('habit-edit-difficulty').value;
        const startDate = document.getElementById('habit-edit-start-date').value;
        const repeatType = document.getElementById('habit-edit-repeat-type').value;
        const repeatEvery = parseInt(document.getElementById('habit-edit-repeat-every').value) || 1;
        // Собираем выбранные дни недели
        const repeatDays = [];
        document.querySelectorAll('#modal-habit-edit .day-toggle.active').forEach(btn => {
            repeatDays.push(parseInt(btn.dataset.day));
        });
        // streak (серия) можно получить из бейджа, если нужно
        let streak = 0;
        const streakBadge = document.querySelector('#modal-habit-edit .habit-streak-badge');
        if (streakBadge) {
            const match = streakBadge.textContent.match(/\d+/);
            if (match) streak = parseInt(match[0]);
        }
        if (title && habitId) {
            fetch('/update_habit_details', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    habit_id: habitId,
                    title: title,
                    notes: notes,
                    difficulty: difficulty,
                    start_date: startDate,
                    repeat_type: repeatType,
                    repeat_every: repeatEvery,
                    repeat_days: repeatDays.join(','),
                    streak: streak
                })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) location.reload();
                    else alert('Ошибка при сохранении привычки');
                });
        } else {
            alert('Название привычки обязательно');
        }
    };

    // Удаление привычки
    if (habitDeleteBtn) habitDeleteBtn.onclick = function () {
        const habitId = document.getElementById('habit-edit-id').value;
        if (confirm('Вы уверены, что хотите удалить эту привычку?') && habitId) {
            fetch('/delete_habit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ habit_id: habitId })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) location.reload();
                    else alert('Ошибка при удалении привычки');
                });
        }
    };

    // Создание привычки
    if (habitCreateBtn) habitCreateBtn.onclick = function () {
        const title = document.getElementById('habit-title').value.trim();
        const notes = document.getElementById('habit-notes').value.trim();
        const difficulty = document.getElementById('habit-difficulty').value;
        const startDate = document.getElementById('habit-start-date').value;
        const repeatType = document.getElementById('habit-repeat-type').value;
        const repeatEvery = parseInt(document.getElementById('habit-repeat-every').value) || 1;

        // Собираем выбранные дни недели
        const repeatDays = [];
        document.querySelectorAll('.day-toggle.active').forEach(btn => {
            repeatDays.push(parseInt(btn.dataset.day));
        });

        if (title) {
            fetch('/add_habit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: title,
                    notes: notes,
                    difficulty: difficulty,
                    start_date: startDate,
                    repeat_type: repeatType,
                    repeat_every: repeatEvery,
                    repeat_days: repeatDays.join(',')
                })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) location.reload();
                    else alert('Ошибка при создании привычки');
                });
        } else {
            alert('Название привычки обязательно');
        }
    };

    // Обработчики для кнопок дней недели — работают через класс .active
    document.querySelectorAll('.day-toggle').forEach(btn => {
        btn.addEventListener('click', function () {
            this.classList.toggle('active');
        });
    });

    // Обновление текста периода повторения
    const repeatTypeSelect = document.getElementById('habit-repeat-type');
    const repeatLabel = document.getElementById('habit-repeat-label');
    if (repeatTypeSelect && repeatLabel) {
        repeatTypeSelect.addEventListener('change', function () {
            const labels = {
                'daily': 'день',
                'weekly': 'неделю',
                'monthly': 'месяц',
                'yearly': 'год'
            };
            repeatLabel.textContent = labels[this.value] || 'неделю';
        });
    }


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
