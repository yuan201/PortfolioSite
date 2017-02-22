from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.views.generic import FormView
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404

from core.mixins import TitleHeaderMixin
from .models import Security
from quotes.models import Quote
from quotes.forms import QuotesFormHorizontal


ITEMS_PER_PAGE = 15


class SecCreateView(TitleHeaderMixin, CreateView):
    template_name = 'security/add_update_sec.html'
    fields = ['symbol', 'currency', 'exchange', 'isindex']
    model = Security

    # todo need to refactor the templates to get rid of jumbotron
    def __init__(self, *args, **kwargs):
        super(SecCreateView, self).__init__(*args, **kwargs)
        self.title = 'Security'
        self.header = 'Add New Security'


class SecListView(TitleHeaderMixin, ListView):
    model = Security
    template_name = 'security/sec_list.html'
    paginate_by = ITEMS_PER_PAGE

    def __init__(self, *args, **kwargs):
        super(SecListView, self).__init__(*args, **kwargs)
        self.title = 'Securities'
        self.header = 'All Securities'


class SecDelView(DeleteView):
    model = Security
    template_name = 'common/delete_confirm.html'
    # todo figure out when should use reverse_lazy instead of reverse
    success_url = reverse_lazy('securities:list')

    # todo check admin site for this, nice to have the ability to delete multiple records
    def get_context_data(self, **kwargs):
        context = super(SecDelView, self).get_context_data(**kwargs)
        context['confirm_title'] = 'Delete Security'
        context['confirm_msg'] = r'<p>Confirm Delete<p><h3>{}</h3>'.format(
            self.object.as_p()
        )
        return context


class SecUpdateView(TitleHeaderMixin, UpdateView):
    model = Security
    fields = ['symbol', 'currency', 'exchange', 'isindex']
    template_name = 'security/add_update_sec.html'

    def __init__(self, *args, **kwargs):
        super(SecUpdateView, self).__init__(*args, **kwargs)
        self.title = 'Security'
        self.header = 'Update Security'


class SecDetailView(TitleHeaderMixin, FormView):
    """
    View to display security details including:
    1. basic info such as name, symbol, currency, etc
    2. recent quotes
    3. an inline form to update quotes
    """
    template_name = 'security/sec_detail.html'
    form_class = QuotesFormHorizontal

    def __init__(self, *args, **kwargs):
        super(SecDetailView, self).__init__(*args, **kwargs)
        self.title = 'Security'
        self.header = ''

    def get_success_url(self, **kwargs):
        sec = get_object_or_404(Security, pk=self.kwargs['pk'])
        return reverse_lazy('securities:detail', args=[sec.id])

    def get_context_data(self, **kwargs):
        context = super(SecDetailView, self).get_context_data(**kwargs)
        # todo get all data to view and use js to filter
        # todo might use AJAX to update data based on user input
        sec = get_object_or_404(Security, pk=self.kwargs['pk'])
        context['quotes'] = Quote.objects.filter(security=sec).order_by('-date').all()[:10]
        context['security'] = sec
        return context

    def get_form_kwargs(self):
        kwargs = super(SecDetailView, self).get_form_kwargs()
        kwargs['security'] = get_object_or_404(Security, pk=self.kwargs['pk'])
        return kwargs

    # todo move business logic to form class
    def form_valid(self, form):
        form.save_quotes()
        return super(SecDetailView, self).form_valid(form)
