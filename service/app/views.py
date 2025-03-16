from django.views.generic import ListView, CreateView, DeleteView, UpdateView, FormView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Task
from .forms import RegistrationForm
from datetime import datetime

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return self.request.user.tasks.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'create_task.html'
    fields = ['title', 'description', 'status', 'due_date']
    success_url = reverse_lazy('app:tasks')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        if not form.instance.title:
            form.add_error('title', 'Title is required')
            return self.form_invalid(form)
        due_date_str = self.request.POST.get('due_date')
        if due_date_str:
            try:
                form.instance.due_date = datetime.strptime(due_date_str, '%Y-%m-%d %H:%M')
            except ValueError:
                form.add_error('due_date', 'Invalid date/time format. Use YYYY-MM-DD HH:MM')
                return self.form_invalid(form)
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form, user=self.request.user))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('app:tasks')

    def get_queryset(self):
        return Task.objects.filter(created_by=self.request.user)

    def get(self, request, *args, **kwargs):
        return redirect('app:tasks')

class TaskUpdateStatusView(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = 'update_task_status.html'
    fields = ['status', 'due_date']
    success_url = reverse_lazy('app:tasks')

    def get_queryset(self):
        return Task.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        new_status = form.cleaned_data['status']
        if new_status not in [choice[0] for choice in Task._meta.get_field('status').choices]:
            form.add_error('status', 'Invalid status')
            return self.form_invalid(form)
        due_date_str = self.request.POST.get('due_date')
        if due_date_str:
            try:
                form.instance.due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                form.add_error('due_date', 'Invalid date/time format')
                return self.form_invalid(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task'] = self.get_object()
        return context

class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('app:login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context