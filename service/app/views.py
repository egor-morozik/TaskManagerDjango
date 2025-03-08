from django.shortcuts import render, redirect
from .models import User

# app/views.py
from django.shortcuts import render, redirect
from .models import User, Task
from django.http import HttpResponseRedirect

def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            return HttpResponseRedirect('/login/')
        return view_func(request, *args, **kwargs)
    return wrapper

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not email or not password:
            return render(request, 'register.html', {'error': 'Email and password are required'})
        try:
            User.objects.create_user(email=email, password=password)
            return redirect('app:login')
        except ValueError:
            return render(request, 'register.html', {'error': 'Email is required'})
        except:
            return render(request, 'register.html', {'error': 'This email is already taken'})
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                request.session['user_id'] = user.id
                return redirect('app:tasks')
            else:
                return render(request, 'login.html', {'error': 'Wrong password'})
        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'User not found'})
    return render(request, 'login.html')

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
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        status = request.POST.get('status')
        user_id = request.session['user_id']
        user = User.objects.get(id=user_id)
        if not title:
            return render(request, 'create_task.html', {'error': 'Title is required', 'user': user})
        Task.objects.create(
            title=title,
            description=description if description else '',
            status=status if status else 'TODO',
            created_by=user
        )
        return redirect('app:tasks')
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
    return render(request, 'create_task.html', {'user': user})

@login_required
def delete_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id, created_by_id=request.session['user_id'])
        task.delete()
        return redirect('app:tasks')
    except Task.DoesNotExist:
        return redirect('app:tasks')