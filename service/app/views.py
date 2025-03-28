from django.views import View
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, FormView, TemplateView, DetailView, RedirectView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache  # Импортируем кэш для работы с Redis
from .models import Task
from .forms import RegistrationForm, TaskForm  
from datetime import datetime, timedelta
from django.http import JsonResponse
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import calendar
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.views import View
from django.shortcuts import redirect


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks.html'
    context_object_name = 'tasks'
    paginate_by = 5

    def get_queryset(self):
        sort_by = self.request.GET.get('sort_by', 'due_date')
        sort_order = self.request.GET.get('sort_order', 'asc')
        search_title = self.request.GET.get('search_title', '').strip()
        search_date = self.request.GET.get('search_date', 'all')
        page = self.request.GET.get('page', '1')

        cache_key = f"task_list:user_{self.request.user.id}:sort_{sort_by}:{sort_order}:search_title_{search_title}:search_date_{search_date}:page_{page}"

        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data

        queryset = self.request.user.tasks.all()

        if search_title:
            queryset = queryset.filter(title__icontains=search_title)

        if search_date != 'all':
            try:
                search_date_obj = datetime.strptime(search_date, '%Y-%m-%d').date()
                queryset = queryset.filter(due_date__date=search_date_obj)
            except ValueError:
                pass

        if sort_by == 'title':
            queryset = queryset.order_by('title' if sort_order == 'asc' else '-title')
        elif sort_by == 'due_date':
            queryset = queryset.order_by('due_date' if sort_order == 'asc' else '-due_date')

        cache.set(cache_key, queryset, timeout=600)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        tasks = self.get_queryset()
        paginator = Paginator(tasks, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            tasks_paginated = paginator.page(page)
        except PageNotAnInteger:
            tasks_paginated = paginator.page(1)
        except EmptyPage:
            tasks_paginated = paginator.page(paginator.num_pages)
        context['tasks'] = tasks_paginated
        context['paginator'] = paginator
        context['page_obj'] = tasks_paginated

        context['sort_by'] = self.request.GET.get('sort_by', 'due_date')
        context['sort_order'] = self.request.GET.get('sort_order', 'asc')
        context['search_title'] = self.request.GET.get('search_title', '')
        context['search_date'] = self.request.GET.get('search_date', 'all')
        
        context['current_date'] = datetime.now().date()

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

        task.due_date = form.cleaned_data.get('due_date')  
        print(f"Task due_date before save (Create): {task.due_date}")
        task.save()
        print(f"Task due_date after save (Create): {task.due_date}")

        cache.delete_pattern(f"task_list:user_{self.request.user.id}:*")
        cache.delete_pattern(f"calendar:user_{self.request.user.id}:*")

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
        task = self.get_object()
        cache.delete_pattern(f"task_list:user_{self.request.user.id}:*")
        cache.delete(f"task_detail:user_{self.request.user.id}:slug_{task.slug}")
        cache.delete_pattern(f"calendar:user_{self.request.user.id}:*")
        return super().post(request, *args, **kwargs)

class UpdateTaskStatusView(LoginRequiredMixin, View):
    def post(self, request, task_slug):
        try:
            task = Task.objects.get(slug=task_slug, created_by=request.user)
            data = json.loads(request.body)
            new_status = data.get('status')
            if new_status not in [choice[0] for choice in Task._meta.get_field('status').choices]:
                return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
            task.status = new_status
            task.save()

            cache.delete_pattern(f"task_list:user_{self.request.user.id}:*")
            cache.delete(f"task_detail:user_{self.request.user.id}:slug_{task.slug}")
            cache.delete_pattern(f"calendar:user_{self.request.user.id}:*")

            return JsonResponse({'success': True})
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    slug_field = 'slug'
    slug_url_kwarg = 'task_slug'
    template_name = 'task_detail.html'

    def get_object(self, queryset=None):

        cache_key = f"task_detail:user_{self.request.user.id}:slug_{self.kwargs['task_slug']}"
        
        task = cache.get(cache_key)
        
        if task is None:
            task = super().get_object(queryset)
            cache.set(cache_key, task, timeout=600)
        
        return task

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
        
        task.due_date = form.cleaned_data.get('due_date') 
        print(f"Task due_date before save (Update): {task.due_date}")
        task.save()
        print(f"Task due_date after save (Update): {task.due_date}")

        cache.delete_pattern(f"task_list:user_{self.request.user.id}:*")
        cache.delete(f"task_detail:user_{self.request.user.id}:slug_{task.slug}")
        cache.delete_pattern(f"calendar:user_{self.request.user.id}:*")

        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        task = self.get_object()
        if task.due_date:
            initial['due_date'] = task.due_date.date()
            initial['due_time'] = task.due_date.time()
        return initial

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
    
class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        year = int(self.request.GET.get('year', datetime.now().year))
        month = int(self.request.GET.get('month', datetime.now().month))

        cache_key = f"calendar:user_{self.request.user.id}:year_{year}:month_{month}"
        tasks_by_day = cache.get(cache_key)

        if tasks_by_day is None:
            tasks = self.request.user.tasks.filter(due_date__year=year, due_date__month=month)
            tasks_by_day = {}
            for task in tasks:
                day = task.due_date.day
                if day not in tasks_by_day:
                    tasks_by_day[day] = []
                tasks_by_day[day].append({
                    'title': task.title,
                    'due_date': task.due_date.strftime('%H:%M'),
                    'slug': task.slug
                })
            for day in tasks_by_day:
                tasks_by_day[day].sort(key=lambda x: x['due_date'])
            cache.set(cache_key, tasks_by_day, timeout=600)

        cal = calendar.monthcalendar(year, month)
        prev_date = datetime(year, month, 1) - timedelta(days=1)
        next_date = datetime(year, month, 1) + timedelta(days=31)

        context['months'] = range(1, 13) 
        context['years'] = range(2000, 2051) 
        context['calendar'] = cal
        context['year'] = year
        context['month'] = month
        context['month_name'] = calendar.month_name[month]
        context['tasks_by_day'] = tasks_by_day
        context['prev_year'] = prev_date.year
        context['prev_month'] = prev_date.month
        context['next_year'] = next_date.year
        context['next_month'] = next_date.month
        context['current_date'] = datetime.now().date()

        return context