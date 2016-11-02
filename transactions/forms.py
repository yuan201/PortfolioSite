from django import forms
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import Submit

from .models import BuyTransaction, SellTransaction, DividendTransaction, SplitTransaction, Transaction2
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


class BuyTxnUpdateForm(forms.ModelForm):
    """
    BuyTxnUpdateForm is used to update an existing buy transaction
    """
    model = BuyTransaction

    class Meta:
        model = BuyTransaction
        fields = ('security', 'datetime', 'price', 'shares', 'fee')


class BuyTxnCreateForm(TxnFormMixin, BuyTxnUpdateForm):
    """
    BuyTxnCreateFrom is used to create a new buy transaction.
    """
    def clean(self):
        cleaned_data = super(BuyTxnCreateForm, self).clean()
        self.check_duplicate_txn(cleaned_data, BuyTransaction)
        return cleaned_data


class SellTxnUpdateForm(forms.ModelForm):
    """
    SellTxnUpdateForm is used to update an existing sell transaction.
    """
    model = SellTransaction

    class Meta:
        model = SellTransaction
        fields = ('security', 'datetime', 'price', 'shares', 'fee')


class SellTxnCreateForm(TxnFormMixin, SellTxnUpdateForm):
    """
    SellTxnCreateForm is used to create a new sell transaction.
    """
    def clean(self):
        cleaned_data = super(SellTxnCreateForm, self).clean()
        self.check_duplicate_txn(cleaned_data, SellTransaction)
        return cleaned_data


class DividendTxnUpdateForm(forms.ModelForm):
    """
    DividendTxnUpdateForm is used to update an existing dividend transaction.
    """
    model = DividendTransaction

    class Meta:
        model = DividendTransaction
        fields = ('security', 'datetime', 'value')


class DividendTxnCreateForm(TxnFormMixin, DividendTxnUpdateForm):
    """
    DividendTxnCreateForm is used to create a new dividend transaction.
    """
    def clean(self):
        cleaned_data = super(DividendTxnCreateForm, self).clean()
        self.check_duplicate_txn(cleaned_data, DividendTransaction)
        return cleaned_data


class SplitTxnUpdateForm(forms.ModelForm):
    """
    SplitTxnUpdateForm is used to update an existing split transaction.
    """
    model = SplitTransaction

    class Meta:
        model = SplitTransaction
        fields = ('security', 'datetime', 'ratio')


class SplitTxnCreateForm(TxnFormMixin, SplitTxnUpdateForm):
    """
    SplitTxnCreateForm is used to create a new split transaction.
    """
    def clean(self):
        cleaned_data = super(SplitTxnCreateForm, self).clean()
        self.check_duplicate_txn(cleaned_data, SplitTransaction)
        return cleaned_data


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


class TransactionUpdateForm(TxnFormMixin, forms.ModelForm):
    class Meta:
        model = Transaction2
        fields = ('security', 'datetime', 'type', 'price', 'shares', 'fee', 'dividend', 'ratio')


class TransactonCreateForm(TransactionUpdateForm):

    def clean(self):
        cleaned_data = super().clean()
        self.check_duplicate_txn(cleaned_data, Transaction2)

