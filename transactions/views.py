import csv

from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import TemplateView, RedirectView, FormView
from django.core.urlresolvers import reverse, reverse_lazy
from django.forms.models import formset_factory
from django.core.exceptions import ObjectDoesNotExist

from extra_views import FormSetView

from .models import Transaction
from portfolios.models import Portfolio
from securities.models import Security
from .forms import TransactionCreateForm, TransactionUpdateForm, TransactionsUploadForm
from .forms import TransactionFormSet, TransactionCreateMultipleHelper, TransactionCreateMultipleForm
from core.mixins import TitleHeaderMixin


class TxnCreateMixin(object):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        portfolio = get_object_or_404(Portfolio, pk=self.kwargs['pk'])
        context['portfolios'] = portfolio
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['portfolios'] = get_object_or_404(Portfolio, pk=self.kwargs['pk'])
        return kwargs


class TxnTemplateMixin(object):
    template_name = 'transaction/add_update_txn.html'


class TxnDeleteMixin(object):
    template_name = 'common/delete_confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
    form_class = TransactionCreateForm


class CreateMultipleTxnView(TemplateView):
    template_name = 'transaction/create_multiple.html'


class TransactionUploadView(RedirectView):
    def post(self, request, *args, **kwargs):
        portfolio = get_object_or_404(Portfolio, pk=kwargs['pk'])
        form = TransactionsUploadForm(request.POST, request.FILES, portfolios=portfolio)
        if form.is_valid():
            self.save_uploaded_file(request.FILES['file'])
        return super().post(request, *args, **kwargs)

    def save_uploaded_file(self, file):
        with open('transactions.csv', 'wb') as fout:
            fout.write(file.read())

    def get_redirect_url(self, *args, **kwargs):
        portfolio = get_object_or_404(Portfolio, pk=kwargs['pk'])
        return reverse('transactions:add_n', args=[portfolio.id])


class TransactionCreateMultipleView(TxnCreateMixin, FormSetView):
    formset_class = TransactionFormSet
    form_class = TransactionCreateMultipleForm
    template_name = 'transaction/create_multiple.html'
    extra = 0

    def __init__(self, *args, **kwargs):
        self.portfolio = None
        super().__init__(*args, **kwargs)

    def prepare_transactions(self):
        transactions = []
        with open('transactions.csv') as file:
            txn_reader = csv.DictReader(file)
            for row in txn_reader:
                try:
                    security = Security.objects.get(symbol=row['Symbol'][:6])
                except ObjectDoesNotExist:
                    continue

                transactions.append({
                    'type': row['Type'],
                    'datetime': row['Date'],
                    'security': security,
                    'price': row['Price'],
                    'shares': row['Shares'],
                    'fee': row['Fee'],
                    'dividend': row['Dividend'],
                    'ratio': row['Ratio'],
                })
        return transactions

    def post(self, request, *args, **kwargs):
        self.portfolio = get_object_or_404(Portfolio, pk=kwargs['pk'])
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.portfolio = get_object_or_404(Portfolio, pk=kwargs['pk'])
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['helper'] = TransactionCreateMultipleHelper()
        return context

    def get_extra_form_kwargs(self):
        kwargs = super().get_extra_form_kwargs()
        kwargs['portfolios'] = self.portfolio
        return kwargs

    def get_initial(self):
        return self.prepare_transactions()

    def get_success_url(self):
        return self.portfolio.get_absolute_url()

    def formset_valid(self, formset):
        for form in formset:
            form.save()
        return super().formset_valid(formset)

