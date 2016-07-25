from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from .models import BuyTransaction, SellTransaction,DividendTrasaction, SplitTransaction
from portfolio.models import Portfolio


class AddTxnView(TemplateView):
    template_name = 'transaction/add_txn.html'

    def get_context_data(self, **kwargs):
        context = super(AddTxnView, self).get_context_data(**kwargs)
        portfolio = get_object_or_404(Portfolio, pk=self.kwargs['pk'])
        context['portfolio'] = portfolio
        return context


class TxCreateViewBase(CreateView):
    template_name = 'transaction/add_one_txn.html'

    def get_context_data(self, **kwargs):
        context = super(TxCreateViewBase, self).get_context_data(**kwargs)
        portfolio = get_object_or_404(Portfolio, pk=self.kwargs['pk'])
        context['portfolio'] = portfolio
        return context

    def form_valid(self, form):
        new_txn = form.save(commit=False)
        new_txn.portfolio = get_object_or_404(Portfolio, pk=self.kwargs['pk'])
        new_txn.save()
        return super(TxCreateViewBase, self).form_valid(form)


class BuyTxCreateView(TxCreateViewBase):
    model = BuyTransaction
    fields = ['security', 'datetime', 'price', 'shares', 'fee']

    def get_context_data(self, **kwargs):
        context = super(BuyTxCreateView, self).get_context_data(**kwargs)
        context['title'] = 'Buy'
        return context


class SellTxCreateView(TxCreateViewBase):
    model = SellTransaction
    fields = ['security', 'datetime', 'price', 'shares', 'fee']

    def get_context_data(self, **kwargs):
        context = super(SellTxCreateView, self).get_context_data(**kwargs)
        context['title'] = 'Sell'
        return context


class DividendTxCreateView(TxCreateViewBase):
    model = DividendTrasaction
    fields = ['security', 'datetime', 'value']

    def get_context_data(self, **kwargs):
        context = super(DividendTxCreateView, self).get_context_data(**kwargs)
        context['title'] = 'Dividend'
        return context


class SplitTxCreateView(TxCreateViewBase):
    model = SplitTransaction
    fields = ['security', 'datetime', 'ratio']

    def get_context_data(self, **kwargs):
        context = super(SplitTxCreateView, self).get_context_data(**kwargs)
        context['title'] = 'Split'
        return context

