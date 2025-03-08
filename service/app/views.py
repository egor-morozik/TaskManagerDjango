# app/views.py
from django.shortcuts import render, redirect
from .models import User, Task
from django.http import HttpResponseRedirect
from datetime import datetime

def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            return HttpResponseRedirect('/login/')
        return view_func(request, *args, **kwargs)
    return wrapper

def register(request):
    user = None
    if request.session.get('user_id'):
        user = User.objects.get(id=request.session['user_id'])
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not email or not password:
            return render(request, 'register.html', {'error': 'Email and password are required', 'user': user})
        try:
            User.objects.create_user(email=email, password=password)
            return redirect('app:login')
        except ValueError:
            return render(request, 'register.html', {'error': 'Email is required', 'user': user})
        except:
            return render(request, 'register.html', {'error': 'This email is already taken', 'user': user})
    return render(request, 'register.html', {'user': user})

def login_view(request):
    user = None
    if request.session.get('user_id'):
        user = User.objects.get(id=request.session['user_id'])
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                request.session['user_id'] = user.id
                return redirect('app:tasks')
            else:
                return render(request, 'login.html', {'error': 'Wrong password', 'user': user})
        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'User not found', 'user': user})
    return render(request, 'login.html', {'user': user})

def logout_view(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('app:login')

@login_required
def tasks(request):
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
    tasks = user.tasks.all()
    return render(request, 'tasks.html', {'tasks': tasks, 'user': user})

@login_required
def create_task(request):
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
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
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
    try:
        task = Task.objects.get(id=task_id, created_by_id=user_id)
        task.delete()
        return redirect('app:tasks')
    except Task.DoesNotExist:
        return redirect('app:tasks')