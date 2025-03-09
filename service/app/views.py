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
        due_date_str = request.POST.get('due_date')
        if not title:
            return render(request, 'create_task.html', {'error': 'Title is required', 'user': user})
        
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                return render(request, 'create_task.html', {'error': 'Invalid date format. Use YYYY-MM-DD', 'user': user})

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

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('app:login')  # Изменено с 'login' на 'app:login'
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})