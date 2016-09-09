import logging

from django.shortcuts import render
from django.views.generic import FormView
from django.core.urlresolvers import reverse

from .forms import QuotesForm
from securities.models import Security
from core.mixins import TitleHeaderMixin

logger = logging.getLogger('quotes_view')


class GetQuotesView(TitleHeaderMixin, FormView):
    template_name = 'quote/get_quotes.html'
    form_class = QuotesForm

    def __init__(self, *args, **kwargs):
        self.title = 'Get Quotes'

    def get_success_url(self):
        return reverse('securities:detail', args=[self.kwargs['pk']])

    def get_form_kwargs(self):
        sec = Security.objects.get(pk=self.kwargs['pk'])
        kwargs = super(GetQuotesView, self).get_form_kwargs()
        kwargs['security'] = sec
        self.header = 'Get Quotes for {}'.format(sec.name)
        return kwargs

    def form_valid(self, form):
        """
        Save the quotes to database
        :param form:
        :return:
        """
        form.save_quotes()
        return super(GetQuotesView, self).form_valid(form)