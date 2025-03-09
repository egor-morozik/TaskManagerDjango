from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Task
from datetime import datetime
from .forms import RegistrationForm

@login_required
def tasks(request):
    user = request.user
    tasks = user.tasks.all()
    return render(request, 'tasks.html', {'tasks': tasks, 'user': user})

@login_required
def create_task(request):
    user = request.user
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        status = request.POST.get('status')
        due_date_str = request.POST.get('due_date')  # Теперь может содержать время

        if not title:
            return render(request, 'create_task.html', {'error': 'Title is required', 'user': user})
        
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d %H:%M')  # Формат: ГГГГ-ММ-ДД ЧЧ:ММ
            except ValueError:
                return render(request, 'create_task.html', {'error': 'Invalid date/time format. Use YYYY-MM-DD HH:MM', 'user': user})

        Task.objects.create(
            title=title,
            description=description if description else '',
            status=status if status else 'TODO',
            due_date=due_date,
            created_by=user
        )
        return redirect('app:tasks')
    return render(request, 'create_task.html', {'user': user})

@login_required
def delete_task(request, task_id):
    user = request.user
    try:
        task = Task.objects.get(id=task_id, created_by=user)
        task.delete()
        return redirect('app:tasks')
    except Task.DoesNotExist:
        return redirect('app:tasks')

@login_required
def update_task_status(request, task_id):
    user = request.user
    try:
        task = Task.objects.get(id=task_id, created_by=user)
        if request.method == 'POST':
            new_status = request.POST.get('status')
            due_date_str = request.POST.get('due_date')

            if new_status in [choice[0] for choice in Task._meta.get_field('status').choices]:
                task.status = new_status
                if due_date_str:
                    try:
                        task.due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
                    except ValueError:
                        return render(request, 'update_task_status.html', {'task': task, 'error': 'Invalid date/time format'})
                task.save()
            return redirect('app:tasks')
    except Task.DoesNotExist:
        return redirect('app:tasks')
    return render(request, 'update_task_status.html', {'task': task})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('app:login')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})