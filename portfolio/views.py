import datetime

from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404

from .models import Portfolio


class HomePageView(ListView):
    model = Portfolio
    template_name = 'homepage.html'


class PortfolioCreateView(CreateView):
    model = Portfolio
    fields = ['name', 'description']
    template_name = 'new_portfolio.html'


class PortfolioDetailView(DetailView):
    template_name = 'portfolio_detail.html'
    model = Portfolio

    def get_context_data(self, **kwargs):
        context = super(PortfolioDetailView, self).get_context_data(**kwargs)
        portfolio = get_object_or_404(Portfolio, pk=self.kwargs['pk'])
        context['portfolio'] = portfolio
        context['transactions'] = portfolio.transactions()
        context['holdings'] = portfolio.holdings(datetime.datetime.now()).values()
        return context
