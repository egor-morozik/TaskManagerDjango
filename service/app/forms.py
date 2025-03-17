from datetime import datetime
from django import forms
from django.contrib.auth.models import User
from .models import Task
from django import forms
from .models import Task
from datetime import datetime
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
    due_date = forms.SplitDateTimeField(
        required=False,
        input_date_formats=['%Y-%m-%d'],
        input_time_formats=['%H:%M'],
        widget=forms.SplitDateTimeWidget(
            date_attrs={'type': 'date', 'class': 'form-control'},
            time_attrs={'type': 'time', 'class': 'form-control'}
        )
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'due_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.due_date:
            self.fields['due_date'].initial = [self.instance.due_date.date(), self.instance.due_date.time()]
            print(f"Initial due_date set to: {self.fields['due_date'].initial}")

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        print(f"Raw due_date in clean_due_date: {due_date}")
        if due_date is not None:
            if isinstance(due_date, datetime):  
                print(f"due_date is already a datetime object: {due_date}")
                return due_date
            if isinstance(due_date, (list, tuple)) and len(due_date) == 2:
                date_part, time_part = due_date
                print(f"Date part: {date_part}, Time part: {time_part}")
                try:
                    combined_date = datetime.combine(date_part, time_part)
                    print(f"Combined due_date: {combined_date}")
                    return combined_date
                except (ValueError, TypeError) as e:
                    print(f"Error combining due_date: {e}")
                    raise forms.ValidationError("Invalid date or time format. Use YYYY-MM-DD and HH:MM.")
        print("due_date is None, returning None")
        return None