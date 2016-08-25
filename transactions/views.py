from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse, reverse_lazy

from .models import BuyTransaction, SellTransaction,DividendTransaction, SplitTransaction
from portfolio.models import Portfolio
from .forms import BuyTxnCreateForm, SellTxnCreateForm, SplitTxnCreateForm, DividendTxnCreateForm
from .forms import BuyTxnUpdateForm, SellTxnUpdateForm, DividendTxnUpdateForm, SplitTxnUpdateForm


class AddTxnView(TemplateView):
    template_name = 'transaction/add_txn.html'

    def get_context_data(self, **kwargs):
        context = super(AddTxnView, self).get_context_data(**kwargs)
        portfolio = get_object_or_404(Portfolio, pk=self.kwargs['pk'])
        context['portfolio'] = portfolio
        return context


class TxnCreateUpdateMixin(object):
    template_name = 'transaction/add_update_txn.html'

    def get_context_data(self, **kwargs):
        context = super(TxnCreateUpdateMixin, self).get_context_data(**kwargs)
        portfolio = get_object_or_404(Portfolio, pk=self.kwargs['pk'])
        context['portfolio'] = portfolio
        return context

    def form_valid(self, form):
        new_txn = form.save(commit=False)
        new_txn.portfolio = get_object_or_404(Portfolio, pk=self.kwargs['pk'])
        new_txn.save()
        return super(TxnCreateUpdateMixin, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(TxnCreateUpdateMixin, self).get_form_kwargs()
        kwargs['portfolio'] = get_object_or_404(Portfolio, pk=self.kwargs['pk'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(TxnCreateUpdateMixin, self).get_context_data(**kwargs)
        context['title'] = self.title
        context['header'] = self.header
        return context


class BuyTxnCreateUpdateView(TxnCreateUpdateMixin, CreateView):
    model = BuyTransaction
    form_class = BuyTxnCreateForm

    def __init__(self):
        self.title = 'Buy'
        self.header = 'New Buy Transaction'


class SellTxnCreateUpdateView(TxnCreateUpdateMixin, CreateView):
    model = SellTransaction
    form_class = SellTxnCreateForm

    def __init__(self):
        self.title = 'Sell'
        self.header = 'New Sell Transaction'


class DividendTxnCreateUpdateView(TxnCreateUpdateMixin, CreateView):
    model = DividendTransaction
    form_class = DividendTxnCreateForm

    def __init__(self):
        self.title = 'Dividend'
        self.header = 'New Dividend Transaction'


class SplitTxnCreateUpdateView(TxnCreateUpdateMixin, CreateView):
    model = SplitTransaction
    form_class = SplitTxnCreateForm

    def __init__(self):
        self.title = 'Split'
        self.header = 'New Split Transaction'


class TxnDeleteMixin(object):
    template_name = 'common/delete_confirm.html'

    def get_context_data(self, **kwargs):
        context = super(TxnDeleteMixin, self).get_context_data(**kwargs)
        context['confirm_title'] = 'Delete Transaction'
        context['confirm_msg'] = r'<p>Confirm Delete<p><h3>{}</h3>'.format(
            self.object.as_p())
        return context

    def get_success_url(self):
        return reverse('portfolios:detail', args=[self.object.portfolio.id])


class BuyTxnDeleteView(TxnDeleteMixin, DeleteView):
    model = BuyTransaction


class SellTxnDeleteView(TxnDeleteMixin, DeleteView):
    model = SellTransaction


class DividendTxnDeleteView(TxnDeleteMixin, DeleteView):
    model = DividendTransaction


class SplitTxnDeleteView(TxnDeleteMixin, DeleteView):
    model = SplitTransaction


class BuyTxnUpdateView(TxnCreateUpdateMixin, UpdateView):
    model = BuyTransaction
    form_class = BuyTxnUpdateForm

    def __init__(self):
        self.title = 'Buy'
        self.header = 'Update Buy Transaction'


class SellTxnUpdateView(TxnCreateUpdateMixin, UpdateView):
    model = SellTransaction
    form_class = SellTxnUpdateForm

    def __init__(self):
        self.title = 'Sell'
        self.header = 'Update Sell Transaction'


class DividendTxnUpdateView(TxnCreateUpdateMixin, UpdateView):
    model = DividendTransaction
    form_class = DividendTxnUpdateForm

    def __init__(self):
        self.title = 'Dividend'
        self.header = 'Update Dividend Transaction'


class SplitTxnUpdateView(TxnCreateUpdateMixin, UpdateView):
    model = SplitTransaction
    form_class = SplitTxnUpdateForm

    def __init__(self):
        self.title = 'Split'
        self.header = 'Update Split Transaction'

