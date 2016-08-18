from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse, reverse_lazy

from .models import BuyTransaction, SellTransaction,DividendTrasaction, SplitTransaction
from portfolio.models import Portfolio
from .forms import BuyTxnCreateForm, SellTxnCreateForm, SplitTxnCreateForm, DividendTxnCreateForm


class AddTxnView(TemplateView):
    template_name = 'transaction/add_txn.html'

    def get_context_data(self, **kwargs):
        context = super(AddTxnView, self).get_context_data(**kwargs)
        portfolio = get_object_or_404(Portfolio, pk=self.kwargs['pk'])
        context['portfolio'] = portfolio
        return context


class TxnCreateViewBase(CreateView):
    template_name = 'transaction/add_one_txn.html'

    def get_context_data(self, **kwargs):
        context = super(TxnCreateViewBase, self).get_context_data(**kwargs)
        portfolio = get_object_or_404(Portfolio, pk=self.kwargs['pk'])
        context['portfolio'] = portfolio
        return context

    def form_valid(self, form):
        new_txn = form.save(commit=False)
        new_txn.portfolio = get_object_or_404(Portfolio, pk=self.kwargs['pk'])
        new_txn.save()
        return super(TxnCreateViewBase, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(TxnCreateViewBase, self).get_form_kwargs()
        kwargs['portfolio'] = get_object_or_404(Portfolio, pk=self.kwargs['pk'])
        return kwargs


class BuyTxnCreateView(TxnCreateViewBase):
    model = BuyTransaction
    form_class = BuyTxnCreateForm

    def get_context_data(self, **kwargs):
        context = super(BuyTxnCreateView, self).get_context_data(**kwargs)
        context['title'] = 'Buy'
        return context


class SellTxnCreateView(TxnCreateViewBase):
    model = SellTransaction
    form_class = SellTxnCreateForm

    def get_context_data(self, **kwargs):
        context = super(SellTxnCreateView, self).get_context_data(**kwargs)
        context['title'] = 'Sell'
        return context


class DividendTxnCreateView(TxnCreateViewBase):
    model = DividendTrasaction
    form_class = DividendTxnCreateForm

    def get_context_data(self, **kwargs):
        context = super(DividendTxnCreateView, self).get_context_data(**kwargs)
        context['title'] = 'Dividend'
        return context


class SplitTxnCreateView(TxnCreateViewBase):
    model = SplitTransaction
    form_class = SplitTxnCreateForm

    def get_context_data(self, **kwargs):
        context = super(SplitTxnCreateView, self).get_context_data(**kwargs)
        context['title'] = 'Split'
        return context


class TxnDeleteViewBase(DeleteView):
    template_name = 'common/delete_confirm.html'

    def get_context_data(self, **kwargs):
        context = super(TxnDeleteViewBase, self).get_context_data(**kwargs)
        context['confirm_title'] = 'Delete Transaction'
        context['confirm_msg'] = r'<p>Confirm Delete<p><h3>{}</h3>'.format(
            self.object.as_p())
        return context

    def get_success_url(self):
        return reverse('portfolios:detail', args=[self.object.portfolio.id])


class BuyTxnDeleteView(TxnDeleteViewBase):
    model = BuyTransaction


class SellTxnDeleteView(TxnDeleteViewBase):
    model = SellTransaction


class DividendTxnDeleteView(TxnDeleteViewBase):
    model = DividendTrasaction


class SplitTxnDeleteView(TxnDeleteViewBase):
    model = SplitTransaction

