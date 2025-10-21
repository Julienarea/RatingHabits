document.addEventListener('DOMContentLoaded', function () {
    // Обработка изменения статуса задачи
    document.querySelectorAll('.task-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            const title = this.dataset.taskTitle;
            const status = this.checked ? 'выполнено' : 'в процессе';

            fetch('/update_task', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: title,
                    status: status
                })
            })
                .then(res => res.json())
                .then(data => {
                    if (!data.success) {
                        this.checked = !this.checked; // возвращаем предыдущее состояние
                        alert('Ошибка при обновлении статуса задачи');
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
    // Обработка изменения статуса привычки
    document.querySelectorAll('.habit-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            const title = this.dataset.habitTitle;
            const currentStreak = parseInt(this.closest('.habit-item').querySelector('.habit-streak').textContent.match(/\d+/)[0]);
            const newStreak = this.checked ? currentStreak + 1 : Math.max(0, currentStreak - 1);

            fetch('/update_habit_streak', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: title,
                    streak: newStreak
                })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        this.closest('.habit-item').querySelector('.habit-streak').textContent = `(Серия: ${newStreak})`;
                    } else {
                        this.checked = !this.checked;
                        alert('Ошибка при обновлении привычки');
                    }
                });
        });
    });
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

    document.querySelectorAll('.filter').forEach(item => {
        item.addEventListener('click', function () {
            // Убираем класс 'active' у всех
            document.querySelectorAll('.filter').forEach(el => el.classList.remove('active'));
            // Добавляем 'active' текущему
            this.classList.add('active');
            console.log('Выбран фильтр:', this.textContent.trim());
        });
    });
});
