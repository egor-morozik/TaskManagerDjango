from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('tasks/', views.tasks, name='tasks'),
    path('create-task/', views.create_task, name='create_task'),
]