import datetime as dt
import pandas as pd
import json

from django.shortcuts import render
from django.views.generic import TemplateView, RedirectView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers

from .models import Portfolio, Holding
from core.mixins import PortfoliosMixin
from todos.models import Todo
from transactions.forms import TransactionsUploadForm
from core.utils import last_business_day


class HomePageView(LoginRequiredMixin, TemplateView):
    # todo figure out a way to test w/ and w/o login user
    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['todo'] = Todo
        return context


class PortfolioCreateView(CreateView):
    model = Portfolio
    fields = ['name', 'description', 'owner']
    template_name = 'portfolio/new_portfolio.html'


class PortfolioDetailView(TemplateView):
    template_name = 'portfolio/portfolio_detail.html'

    # todo add performance for this year, last year, last month
    # todo add performance chart
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        portfolio = get_object_or_404(Portfolio, pk=self.kwargs['pk'])
        context['portfolio'] = portfolio
        context['transactions'] = portfolio.transactions.all()
        context['upload_form'] = TransactionsUploadForm(portfolios=portfolio)
        # quick test
        Holding.update_all_values(portfolio)
        context['position'] = portfolio.position(date=last_business_day())
        context['performance'] = portfolio.performance.order_by('-date').all()[:10]
        return context


class PortfolioListView(ListView):
    model = Portfolio
    template_name = 'portfolio/portfolio_list.html'


class PortfolioUpdatePerfView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        portfolio = get_object_or_404(Portfolio, pk=kwargs['pk'])
        return portfolio.get_absolute_url()

    def get(self, request, *args, **kwargs):
        portfolio = get_object_or_404(Portfolio, pk=kwargs['pk'])
        portfolio.performance.all().delete()
        portfolio.update_performance()
        return super().get(request, *args, **kwargs)


class PortfolioHoldingUpdateView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        portfolio = get_object_or_404(Portfolio, pk=kwargs['pk'])
        return portfolio.get_absolute_url()

    def get(self, request, *args, **kwargs):
        portfolio = get_object_or_404(Portfolio, pk=kwargs['pk'])
        portfolio.remove_all_holdings()
        portfolio.update_holdings()
        return super().get(request, *args, **kwargs)


class PortfolioChartView(TemplateView):
    # todo make other data available for charts (benchmark, gain, etc.)
    # todo refactor chart js code to show multiple charts
    # todo clean up code for charts
    template_name = 'portfolio/portfolio_chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        portfolio = get_object_or_404(Portfolio, pk=self.kwargs['pk'])
        values = []
        for p in portfolio.performance.order_by('date').filter(date__gt=dt.date(2016,1,1)).all():
            values.append({'date': p.date.isoformat(), 'value': float(p.value)})

        context['values'] = json.dumps(values)
        return context
