import datetime as dt

from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404
import pandas as pd

from .models import Portfolio, Holding
from core.mixins import PortfoliosMixin
from todos.models import Todo


class HomePageView(ListView):
    model = Portfolio
    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['todo'] = Todo
        return context


class PortfolioCreateView(CreateView):
    model = Portfolio
    fields = ['name', 'description']
    template_name = 'portfolio/new_portfolio.html'


class PortfolioDetailView(DetailView):
    template_name = 'portfolio/portfolio_detail.html'
    model = Portfolio

    def get_context_data(self, **kwargs):
        context = super(PortfolioDetailView, self).get_context_data(**kwargs)
        portfolio = get_object_or_404(Portfolio, pk=self.kwargs['pk'])
        context['portfolios'] = portfolio
        context['transactions'] = portfolio.transactions()
        # quick test
        portfolio.update_holdings(pd.Timestamp(dt.date.today()))
        context['holdings'] = [Holding.objects.filter(portfolio=portfolio).last()]
        return context


class PortfolioListView(ListView):
    model = Portfolio
    template_name = 'portfolio/portfolio_list.html'




