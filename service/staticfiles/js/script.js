document.addEventListener('DOMContentLoaded', () => {

    const taskItems = document.querySelectorAll('.task-item');
    taskItems.forEach((item, index) => {
        setTimeout(() => {
            item.classList.add('visible');
        }, index * 100);
    });

    const fadeInElements = document.querySelectorAll('.fade-in');
    fadeInElements.forEach(element => {
        element.classList.add('visible');
    });

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