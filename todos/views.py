from django.shortcuts import render
from django.views.generic import CreateView, UpdateView

from .models import Todo


class TodoCreateView(CreateView):
    model = Todo
    template_name = 'todo/todo_create_update.html'
    fields = ['title', 'slug', 'content', 'parent', 'status']


class TodoUpdateView(UpdateView):
    model = Todo
    template_name = 'todo/todo_create_update.html'
    fields = ['title', 'slug', 'content', 'parent', 'status']

