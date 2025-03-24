from datetime import datetime
from django import forms
from django.contrib.auth.models import User
from .models import Task

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class TaskForm(forms.ModelForm):
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label="Due Date"
    )
    due_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        required=False,
        label="Due Time"
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'due_time']

    def clean(self):
        cleaned_data = super().clean()
        due_date = cleaned_data.get('due_date')
        due_time = cleaned_data.get('due_time')

        if due_date and due_time:
            try:
                due_datetime = datetime.combine(due_date, due_time)
                cleaned_data['due_date'] = due_datetime
            except ValueError as e:
                self.add_error('due_time', 'Enter a valid time.')
        elif due_date and not due_time:
           cleaned_data['due_date'] = datetime.combine(due_date, datetime.min.time())
        elif due_time and not due_date:
            self.add_error('due_date', 'Please specify a due date if a time is provided.')

        return cleaned_data