from django.db import models
from django.core.urlresolvers import reverse


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

    def get_absolute_url(self):
        return reverse('home')

    def to_table(self, item):
        result = '<li class=todo-{status}><a href="{link}">{title}</a>'.format(
            link=reverse('todos:update', args=[item.id]), title=item.title, status=item.status)
        if item.children:
            result += '<ul>'
            for child in item.children.all():
                if child == item:
                    break
                result += self.to_table(child)
            result += '</ul>'
        result += '</li>'
        return result

    def inactive_as_l(self):
        return self.todos_as_l('inactive')

    def active_as_l(self):
        return self.todos_as_l('active')

    def done_as_l(self):
        return self.todos_as_l('done')

    def todos_as_l(self, status):
        result = ""
        for item in Todo.objects.filter(status=status).filter(parent__isnull=True).all():
            result += self.to_table(item)
        return result

    def __str__(self):
        return self.slug
