# app/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[('TODO', 'To Do'), ('IN_PROGRESS', 'In Progress'), ('DONE', 'Done')])
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return self.title