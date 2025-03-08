# app/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _

class UserManager(models.Manager):
    def create_user(self, email, password):
        if not email:
            raise ValueError(_('The Email field must be set'))
        user = self.model(email=email, password=password)
        user.save(using=self._db)
        return user

class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    objects = UserManager()

    def check_password(self, raw_password):
        return self.password == raw_password

    def __str__(self):
        return self.email

class Task(models.Model):
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('DONE', 'Done'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True, help_text="Date when the task should be completed")
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return self.title