// app/static/js/script.js
document.addEventListener('DOMContentLoaded', () => {
    // Анимация для задач
    const taskItems = document.querySelectorAll('.task-item');
    taskItems.forEach((item, index) => {
        setTimeout(() => {
            item.classList.add('visible');
        }, index * 100);
    });

    // Анимация для форм логина и регистрации
    const fadeInElements = document.querySelectorAll('.fade-in');
    fadeInElements.forEach(element => {
        element.classList.add('visible');
    });

    // Простая валидация формы (опционально)
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', (e) => {
            const title = document.querySelector('input[name="title"]');
            if (title && !title.value) {
                e.preventDefault();
                alert('Title is required!');
            }
        });
    }
});