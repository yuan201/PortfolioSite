from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse, reverse_lazy

from .models import Transaction
from portfolios.models import Portfolio
from .forms import TransactonCreateForm, TransactionUpdateForm
from core.mixins import TitleHeaderMixin


class TxnCreateMixin(object):
    def get_context_data(self, **kwargs):
        context = super(TxnCreateMixin, self).get_context_data(**kwargs)
        portfolio = get_object_or_404(Portfolio, pk=self.kwargs['pk'])
        context['portfolios'] = portfolio
        return context

    def form_valid(self, form):
        new_txn = form.save(commit=False)
        new_txn.portfolio = get_object_or_404(Portfolio, pk=self.kwargs['pk'])
        new_txn.save()
        return super(TxnCreateMixin, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(TxnCreateMixin, self).get_form_kwargs()
        kwargs['portfolios'] = get_object_or_404(Portfolio, pk=self.kwargs['pk'])
        return kwargs


class TxnTemplateMixin(object):
    template_name = 'transaction/add_update_txn.html'


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


class TransactionUpdateView(TxnTemplateMixin, UpdateView):
    model = Transaction
    template_name = 'transaction/add_update_txn.html'
    form_class = TransactionUpdateForm


class TransactionDelView(TxnDeleteMixin, DeleteView):
    model = Transaction
    template_name = 'common/delete_confirm.html'


class TransactionCreateView(TxnTemplateMixin, TxnCreateMixin, CreateView):
    model = Transaction
    form_class = TransactonCreateForm


class CreateMultipleTxnView(TemplateView):
    template_name = 'transaction/create_multiple.html'