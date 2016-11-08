import csv
import json
import tempfile

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
from .forms import TransactionCreateUpdateForm, TransactionsUploadForm, TransactionCreateMultipleHelper
from core.mixins import TitleHeaderMixin
from .exceptions import UnknownTransactionType


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
    form_class = TransactionCreateUpdateForm


# todo update holdings after removal
class TransactionDelView(TxnDeleteMixin, DeleteView):
    model = Transaction
    template_name = 'common/delete_confirm.html'


class TransactionCreateView(TxnTemplateMixin, TxnCreateMixin, CreateView):
    model = Transaction
    form_class = TransactionCreateUpdateForm


class CreateMultipleTxnView(TemplateView):
    template_name = 'transaction/create_multiple.html'


class TransactionUploadView(RedirectView):
    def post(self, request, *args, **kwargs):
        portfolio = get_object_or_404(Portfolio, pk=kwargs['pk'])
        form = TransactionsUploadForm(request.POST, request.FILES, portfolios=portfolio)
        if form.is_valid():
            # todo support more file format and convert to JSON
            self.save_uploaded_file(request.FILES['file'])
        return super().post(request, *args, **kwargs)

    def save_uploaded_file(self, file):
        if file.name.endswith('csv'):
            self._save_to_temp(file, 'upload_temp.csv')
            with open('temp/upload_temp.csv', 'r') as fin:
                with open('temp/transactions.json', 'w') as fout:
                    csv_reader = csv.DictReader(fin)
                    for row in csv_reader:
                        fout.write(self._csv_to_json(row) + '\n')
        elif file.name.endswith('json'):
            with open('temp/transactions.json', 'wb') as fout:
                fout.write(file.read())

    @staticmethod
    def _save_to_temp(file, tempfile):
        with open('temp/' + tempfile, 'wb') as fout:
            fout.write(file.read())

    @staticmethod
    def _csv_to_json(row):
        txn = {}
        txn['type'] = row['Type']
        txn['datetime'] = row['Date'].strip()
        txn['security'] = row['Symbol'][:6]
        if txn['type']=='buy' or txn['type']=='sell':
            txn['price'] = row['Price'].strip()
            txn['shares'] = row['Shares'].strip()
            txn['fee'] = row['Fee'].strip()
        elif txn['type']=='dividend':
            txn['dividend'] = row['Dividend'].strip()
        elif txn['type']=='split':
            txn['ratio'] = row['Ratio'].strip()
        else:
            raise UnknownTransactionType
        return json.dumps(txn)

    def get_redirect_url(self, *args, **kwargs):
        portfolio = get_object_or_404(Portfolio, pk=kwargs['pk'])
        return reverse('transactions:add_n', args=[portfolio.id])


class TransactionCreateMultipleView(TxnCreateMixin, FormSetView):
    form_class = TransactionCreateUpdateForm
    template_name = 'transaction/create_multiple.html'
    extra = 0

    def __init__(self, *args, **kwargs):
        self.portfolio = None
        super().__init__(*args, **kwargs)

    def prepare_transactions(self):
        transactions = []
        with open('temp/transactions.json') as file:
            for row in file:
                txn = json.loads(row)
                print(txn)
                txn['security'] = get_object_or_404(Security, symbol=txn['security'])
                transactions.append(txn)
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

