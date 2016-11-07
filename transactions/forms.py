import datetime as dt
import pandas as pd

from django import forms
from django.core.urlresolvers import reverse
from django.forms.models import formset_factory

from crispy_forms.helper import FormHelper, Layout
from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import Submit

from .models import Transaction
from .models import Security


class TxnCheckingMixin(object):

    def check_duplicate_txn(self, cleaned_data, txn_cls):
        """
        Use the form message system to report if the transaction to add already
        exists. If another transaction of the same type, for the same security and
        occurs at the same time is found in the system, the new transaction is considered
        a duplicate.
        """
        security = cleaned_data.get('security')
        datetime = cleaned_data.get('datetime')

        if txn_cls.objects.filter(portfolio=self.portfolio).filter(
                security=security).filter(datetime=datetime).count() > 0:
            msg = u"Transaction Already Exists"
            self.add_error(None, msg)

    def check_split_transaction(self, cleaned_data):
        if cleaned_data['type'] == 'split' and cleaned_data['ratio'] <= 0:
            msg = u"Ratio must be >0 for Split Transaction"
            self.add_error('ratio', msg)

    def check_dividend_transaction(self, cleaned_data):
        if cleaned_data['type'] == 'dividend' and cleaned_data['dividend'] <= 0:
            msg = u"Dividend must be >0 for Dividend Transaction"
            self.add_error('ratio', msg)

    def check_buy_sell_transaction(self, cleaned_data):
        type = cleaned_data['type']
        if type == 'buy' or type == 'sell':
            if cleaned_data['price'] <= 0:
                msg = u"Price must be >0 for {} Transaction".format(type.capitalize())
                self.add_error('price', msg)
            if cleaned_data['shares'] <= 0:
                msg = u"Price must be >0 for {} Transaction".format(type.capitalize())
                self.add_error('shares', msg)
            if cleaned_data['fee'] < 0:
                msg = u"Fee must be >=0 for {} Transaction".format(type.capitalize())
                self.add_error('fee', msg)


class TxnCreateMixin(object):
    """
    Mixin class for all transactions create forms. Provide a few common functions.
    """
    def __init__(self, *args, **kwargs):
        """
        When creating the transaction, the portfolios the new transaction belongs to is
        already defined. This parameter is passed in through kwargs.
        """
        self.portfolio = kwargs.pop('portfolios', None)
        super().__init__(*args, **kwargs)


    def save(self, *args, **kwargs):
        txn = super().save(commit=False)

        if self.portfolio:
            txn.portfolio = self.portfolio
        txn.fill_in_defaults()

        txn.portfolio.remove_holdings_after(
            security = self.cleaned_data['security'],
            datetime = self.cleaned_data['datetime'])

        if txn.id:
            original = Transaction.objects.get(pk=txn.id)
            txn.portfolio.remove_holdings_after(
                security=original.security,
                datetime=original.datetime
            )

        txn = super().save(commit=True)
        last_day = pd.Timestamp(dt.date.today(), offset='B') - 1
        txn.portfolio.update_holdings(last_day)
        return txn


class TransactionsUploadForm(TxnCreateMixin, forms.Form):
    """
    UploadTransactionForm let user select a file to upload which contains list of transactions.
    Support file format: CSV
    """
    file = forms.FileField(label='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('transactions:upload', args=[self.portfolio.id])


class TransactionCreateUpdateForm(TxnCheckingMixin, TxnCreateMixin, forms.ModelForm):

    class Meta:
        model = Transaction
        exclude = ['portfolio']
        #fields = ['security', 'datetime', 'type', 'price', 'shares', 'fee', 'dividend', 'ratio']

    def clean(self):
        cleaned_data = super().clean()
        self.check_duplicate_txn(cleaned_data, Transaction)
        self.check_buy_sell_transaction(cleaned_data)
        self.check_dividend_transaction(cleaned_data)
        self.check_split_transaction(cleaned_data)


class TransactionCreateMultipleHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_class = 'form_inline'
        self.add_input(Submit('submit', 'Save'))
        self.template = 'bootstrap/table_inline_formset.html'

