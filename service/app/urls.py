from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'app'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path('tasks/', views.tasks, name='tasks'),
    path('create-task/', views.create_task, name='create_task'),
    path('delete-task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('accounts/profile/', views.profile, name='profile'),
    path('update-task-status/<int:task_id>/', views.update_task_status, name='update_task_status')
]