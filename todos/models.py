from django.db import models
from django.core.urlresolvers import reverse
from django.utils.html import format_html, mark_safe


class Todo(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField()
    content = models.TextField()
    parent = models.ForeignKey('self', blank=True, null=True, related_name="children")
    STATUS_CHOICES = (
        ('inactive', 'Inactive'),
        ('active', 'Active'),
        ('done', 'Done')
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    @staticmethod
    def get_absolute_url():
        return reverse('home')

    @staticmethod
    def to_table(item):
        result = format_html('<li class=todo-{status}><a href="{link}">{title}</a>',
                             status=item.status,
                             link=mark_safe(reverse('todos:update', args=[item.id])),
                             title=item.title)
        if item.children:
            result += '<ul>'
            for child in item.children.all():
                if child == item:
                    break
                result += Todo.to_table(child)
            result += '</ul>'
        result += '</li>'
        return result

    @staticmethod
    def inactive_as_l():
        return Todo.todos_as_l('inactive')

    @staticmethod
    def active_as_l():
        return Todo.todos_as_l('active')

    @staticmethod
    def done_as_l():
        return Todo.todos_as_l('done')

    @staticmethod
    def todos_as_l(status):
        result = ""
        for item in Todo.objects.filter(status=status).filter(parent__isnull=True).all():
            result += Todo.to_table(item)
        return result

    def __str__(self):
        return self.slug
