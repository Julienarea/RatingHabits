document.addEventListener('DOMContentLoaded', function() {
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
        addTaskBtn.addEventListener('click', function() {
            overlay.style.display = 'block';
            modalTask.style.display = 'flex';
            document.getElementById('task-title').focus();
        });
    }
    if (addHabitBtn) {
        addHabitBtn.addEventListener('click', function() {
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
    if (taskCreateBtn) taskCreateBtn.onclick = function() {
        const title = document.getElementById('task-title').value.trim();
        if (title) {
            fetch('/add_task', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({title})
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
    if (habitCreateBtn) habitCreateBtn.onclick = function() {
        const title = document.getElementById('habit-title').value.trim();
        if (title) {
            fetch('/add_habit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({title})
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) location.reload();
                else alert('Ошибка при добавлении привычки');
            });
        }
        closeModals();
    };
});
