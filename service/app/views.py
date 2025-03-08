from django.shortcuts import render, redirect
from .models import User

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not email or not password:
            return render(request, 'register.html', {'error': 'Email and password are required'})
        try:
            User.objects.create_user(email=email, password=password)
            return redirect('login')  
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
                return redirect('tasks')  
            else:
                return render(request, 'login.html', {'error': 'Wrong password'})
        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'User not found'})
    return render(request, 'login.html')

def logout_view(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('login')