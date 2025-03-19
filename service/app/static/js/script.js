document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.mark-complete');
    console.log('Found buttons:', buttons.length);

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');
    console.log('CSRF Token:', csrftoken);

    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.disabled) return; // Предотвращаем повторные клики
            this.disabled = true; // Блокируем кнопку

            const taskSlug = this.dataset.taskSlug;
            const currentStatus = this.dataset.status;
            const newStatus = currentStatus === 'DONE' ? 'TODO' : 'DONE';

            fetch(`/update-task-status/${taskSlug}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ status: newStatus })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    const taskItem = button.closest('.task-item');
                    const taskContent = taskItem.querySelector('.task-content');
                    const taskTitle = taskItem.querySelector('h5');
                    const taskDescription = taskItem.querySelector('p');

                    if (newStatus === 'DONE') {
                        taskContent.classList.add('task-done');
                        taskTitle.classList.add('task-title-done');
                        taskDescription.classList.add('task-description-done');
                    } else {
                        taskContent.classList.remove('task-done');
                        taskTitle.classList.remove('task-title-done');
                        taskDescription.classList.remove('task-description-done');
                    }
                    button.dataset.status = newStatus;
                } else {
                    alert('Error updating status: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                alert('Error: ' + error);
            })
            .finally(() => {
                this.disabled = false; // Разблокируем кнопку
            });
        });
    });
});