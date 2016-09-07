from django.shortcuts import render
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.core.urlresolvers import reverse, reverse_lazy

from core.mixins import TitleHeaderMixin
from .models import Security


class SecCreateView(TitleHeaderMixin, CreateView):
    template_name = 'security/add_update_sec.html'
    fields = ['symbol', 'name', 'currency', 'quoter']
    model = Security

    def __init__(self):
        self.title = 'Security'
        self.header = 'Add New Security'


class SecListView(TitleHeaderMixin, ListView):
    model = Security
    template_name = 'security/sec_list.html'

    def __init__(self):
        self.title = 'Securities'
        self.header = 'All Securities'


class SecDelView(DeleteView):
    model = Security
    template_name = 'common/delete_confirm.html'
    success_url = reverse_lazy('securities:list')

    def get_context_data(self, **kwargs):
        context = super(SecDelView, self).get_context_data(**kwargs)
        context['confirm_title'] = 'Delete Security'
        context['confirm_msg'] = r'<p>Confirm Delete<p><h3>{}</h3>'.format(
            self.object.as_p()
        )
        return context


class SecUpdateView(TitleHeaderMixin, UpdateView):
    model = Security
    fields = ['symbol', 'name', 'currency', 'quoter']
    template_name = 'security/add_update_sec.html'

    def __init__(self):
        self.title = 'Security'
        self.header = 'Update Security'


class SecDetailView(TitleHeaderMixin, DetailView):
    model = Security
    template_name = 'security/sec_detail.html'

    def __init__(self):
        self.title = 'Security'

    def get_context_data(self, **kwargs):
        self.header = self.object.name
        context = super(SecDetailView, self).get_context_data(**kwargs)
        return context
