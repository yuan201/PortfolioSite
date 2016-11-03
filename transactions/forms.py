from django import forms
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import Submit

from .models import Transaction
from .models import Security


class TxnFormMixin():
    """
    Mixin class for all transactions create forms. Provide a few common functions.
    """
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

    def __init__(self, *args, **kwargs):
        """
        When creating the transaction, the portfolios the new transaction belongs to is
        already defined. This parameter is passed in through kwargs.
        """
        self.portfolio = kwargs.pop('portfolios')
        super(TxnFormMixin, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.portfolio.remove_holdings_after(
            security=self.cleaned_data['security'],
            date=self.cleaned_data['datetime'],
        )
        return super(TxnFormMixin, self).save(*args, **kwargs)


class UploadTransactionsForm(forms.Form):
    """
    UploadTransactionForm let user select a file to upload which contains list of transactions.
    Support file format: CSV
    """
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('upload',' Upload'))


class TransactionUpdateForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ('security', 'datetime', 'type', 'price', 'shares', 'fee', 'dividend', 'ratio')


class TransactonCreateForm(TxnFormMixin ,TransactionUpdateForm):

    def clean(self):
        cleaned_data = super().clean()
        self.check_duplicate_txn(cleaned_data, Transaction)


class TransactionUploadFileForm(forms.Form):
    file = forms.FileField()