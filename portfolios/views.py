import datetime as dt

from django.shortcuts import render
from django.views.generic import TemplateView, RedirectView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
import pandas as pd

from .models import Portfolio, Holding
from core.mixins import PortfoliosMixin
from todos.models import Todo
from transactions.forms import TransactionsUploadForm


class HomePageView(LoginRequiredMixin, TemplateView):
    # todo figure out a way to test w/ and w/o login user
    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['todo'] = Todo
        return context


class PortfolioCreateView(CreateView):
    model = Portfolio
    fields = ['name', 'description', 'owner']
    template_name = 'portfolio/new_portfolio.html'


class PortfolioDetailView(TemplateView):
    template_name = 'portfolio/portfolio_detail.html'

    # todo remove quick test and implement this properly
    def get_context_data(self, **kwargs):
        context = super(PortfolioDetailView, self).get_context_data(**kwargs)
        portfolio = get_object_or_404(Portfolio, pk=self.kwargs['pk'])
        context['portfolio'] = portfolio
        context['transactions'] = portfolio.transactions.all()
        context['upload_form'] = TransactionsUploadForm(portfolios=portfolio)
        # quick test
        last_day = pd.Timestamp(dt.date.today(), offset='B')-1
        portfolio.update_holdings(last_day)
        Holding.update_all_values(portfolio)
        context['holdings'] = Holding.objects.filter(portfolio=portfolio).filter(date=last_day)
        return context


class PortfolioListView(ListView):
    model = Portfolio
    template_name = 'portfolio/portfolio_list.html'


