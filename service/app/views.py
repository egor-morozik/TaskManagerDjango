from django.views.generic import ListView, CreateView, DeleteView, UpdateView, FormView, TemplateView, DetailView, RedirectView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Task
from .forms import RegistrationForm, TaskForm  
from datetime import datetime
from django.http import JsonResponse
import json

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
    form_class = TaskForm
    template_name = 'create_task.html'
    success_url = reverse_lazy('app:tasks')

    def post(self, request, *args, **kwargs):
        print(f"Raw POST data (Create): {request.POST}")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        if not form.cleaned_data['title']:
            form.add_error('title', 'Title is required')
            return self.form_invalid(form)
        print(f"Form cleaned_data (Create): {form.cleaned_data}")
        task = form.save(commit=False)
        due_date = form.cleaned_data.get('due_date')
        if due_date:
            task.due_date = due_date
        print(f"Task due_date before save (Create): {task.due_date}")
        task.save()
        print(f"Task due_date after save (Create): {task.due_date}")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
    
class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('app:tasks')
    slug_field = 'slug'
    slug_url_kwarg = 'task_slug'
    template_name = 'task_confirm_delete.html'

    def get_queryset(self):
        return Task.objects.filter(created_by=self.request.user)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class TaskUpdateStatusView(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = 'update_task_status.html'
    fields = ['status', 'due_date']
    success_url = reverse_lazy('app:tasks')
    slug_field = 'slug'
    slug_url_kwarg = 'task_slug'

    def get_queryset(self):
        return Task.objects.filter(created_by=self.request.user)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = json.loads(request.body)
            new_status = data.get('status')

            if new_status not in [choice[0] for choice in Task._meta.get_field('status').choices]:
                return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)

            self.object.status = new_status
            self.object.save()
            return JsonResponse({'success': True})

        return super().post(request, *args, **kwargs)

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

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    slug_field = 'slug'
    slug_url_kwarg = 'task_slug'
    template_name = 'task_detail.html'

    def get_queryset(self):
        return Task.objects.filter(created_by=self.request.user)

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    slug_field = 'slug'
    slug_url_kwarg = 'task_slug'
    template_name = 'task_update.html'
    success_url = reverse_lazy('app:tasks')

    def get_queryset(self):
        return Task.objects.filter(created_by=self.request.user)

    def post(self, request, *args, **kwargs):
        print(f"Raw POST data (Update): {request.POST}")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        if not form.cleaned_data['title']:
            form.add_error('title', 'Title is required')
            return self.form_invalid(form)
        print(f"Form cleaned_data (Update): {form.cleaned_data}")
        task = form.save(commit=False)
        due_date = form.cleaned_data.get('due_date')
        if due_date:
            task.due_date = due_date
        print(f"Task due_date before save (Update): {task.due_date}")
        task.save()
        print(f"Task due_date after save (Update): {task.due_date}")
        return super().form_valid(form)

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

class RootRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return reverse_lazy('app:tasks')
        return reverse_lazy('app:login')