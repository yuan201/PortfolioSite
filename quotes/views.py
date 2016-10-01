import logging

from django.shortcuts import render
from django.views.generic import FormView
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from .forms import QuotesForm
from securities.models import Security
from core.mixins import TitleHeaderMixin

logger = logging.getLogger('quotes_view')


class GetQuotesView(TitleHeaderMixin, FormView):
    template_name = 'quote/get_quotes.html'
    form_class = QuotesForm

    def __init__(self, *args, **kwargs):
        super(GetQuotesView, self).__init__(*args, **kwargs)
        self.title = 'Get Quotes'

    def get_success_url(self):
        return reverse('securities:detail', args=[self.kwargs['pk'],])

    # todo I believe there are 3rd party packages to handle this
    def get_form_kwargs(self):
        sec = get_object_or_404(Security, self.kwargs['pk'])
        kwargs = super(GetQuotesView, self).get_form_kwargs()
        kwargs['security'] = sec
        self.header = 'Get Quotes for {}'.format(sec.name)
        return kwargs

    # todo move business logic to form class instead of view class
    def form_valid(self, form):
        """
        Save the quotes to database
        """
        form.save_quotes()
        return super(GetQuotesView, self).form_valid(form)
