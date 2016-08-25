from django import forms

from .models import BuyTransaction, SellTransaction, DividendTransaction, SplitTransaction
from .models import Security


class TxnFormMixin():

    def check_duplicate_txn(self, cleaned_data, txn_cls):
        security = cleaned_data.get('security')
        datetime = cleaned_data.get('datetime')

        if txn_cls.objects.filter(portfolio=self.portfolio).filter(
            security=security).filter(datetime=datetime).count() > 0:
            msg = u"Transaction Already Exists"
            self.add_error(None, msg)

    def __init__(self, **kwargs):
        self.portfolio = kwargs.pop('portfolio')
        super().__init__(**kwargs)


class BuyTxnUpdateForm(TxnFormMixin, forms.ModelForm):

    model = BuyTransaction

    class Meta:
        model = BuyTransaction
        fields = ('security', 'datetime', 'price', 'shares', 'fee')


class BuyTxnCreateForm(BuyTxnUpdateForm):

    def clean(self):
        cleaned_data = super().clean()
        self.check_duplicate_txn(cleaned_data, BuyTransaction)
        return cleaned_data


class SellTxnUpdateForm(TxnFormMixin, forms.ModelForm):

    model = SellTransaction

    class Meta:
        model = SellTransaction
        fields = ('security', 'datetime', 'price', 'shares', 'fee')


class SellTxnCreateForm(SellTxnUpdateForm):

    def clean(self):
        cleaned_data = super().clean()
        self.check_duplicate_txn(cleaned_data, SellTransaction)
        return cleaned_data


class DividendTxnUpdateForm(TxnFormMixin, forms.ModelForm):

    model = DividendTransaction

    class Meta:
        model = DividendTransaction
        fields = ('security', 'datetime', 'value')


class DividendTxnCreateForm(DividendTxnUpdateForm):

    def clean(self):
        cleaned_data = super().clean()
        self.check_duplicate_txn(cleaned_data, DividendTransaction)
        return cleaned_data


class SplitTxnUpdateForm(TxnFormMixin, forms.ModelForm):

    model = SplitTransaction

    class Meta:
        model = SplitTransaction
        fields = ('security', 'datetime', 'ratio')


class SplitTxnCreateForm(SplitTxnUpdateForm):

    def clean(self):
        cleaned_data = super().clean()
        self.check_duplicate_txn(cleaned_data, SplitTransaction)
        return cleaned_data
