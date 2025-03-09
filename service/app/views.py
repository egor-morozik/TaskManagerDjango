from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Task
from datetime import datetime
from .forms import RegistrationForm
from django.http import JsonResponse

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

@login_required
def update_task_status(request, task_id):
    user = request.user
    try:
        task = Task.objects.get(id=task_id, created_by=user)
        if request.method == 'POST':
            new_status = request.POST.get('status') or request.body.decode('utf-8') and request.POST.get('status')
            if not new_status:
                try:
                    import json
                    data = json.loads(request.body)
                    new_status = data.get('status')
                except json.JSONDecodeError:
                    return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)

            if new_status in [choice[0] for choice in Task._meta.get_field('status').choices]:
                task.status = new_status
                task.save()
                return JsonResponse({'success': True})
            return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
    except Task.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)
    return render(request, 'update_task_status.html', {'task': task})