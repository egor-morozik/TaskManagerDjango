from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'app'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path('tasks/', views.TaskListView.as_view(), name='tasks'),
    path('create-task/', views.TaskCreateView.as_view(), name='create_task'),
    path('delete-task/<slug:task_slug>/', views.TaskDeleteView.as_view(), name='delete_task'),
    path('accounts/profile/', views.ProfileView.as_view(), name='profile'),
    path('update-task-status/<slug:task_slug>/', views.TaskUpdateStatusView.as_view(), name='update_task_status'),
    path('task/<slug:task_slug>/', views.TaskDetailView.as_view(), name='task_detail'),
]