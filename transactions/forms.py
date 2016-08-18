from django import forms

from .models import BuyTransaction, SellTransaction, DividendTrasaction, SplitTransaction
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


class BuyTxnCreateForm(TxnFormMixin, forms.ModelForm):

    class Meta:
        model = BuyTransaction
        fields = ('security', 'datetime', 'price', 'shares', 'fee')

    def clean(self):
        cleaned_data = super().clean()
        self.check_duplicate_txn(cleaned_data, BuyTransaction)
        return cleaned_data


class SellTxnCreateForm(TxnFormMixin, forms.ModelForm):

    class Meta:
        model = SellTransaction
        fields = ('security', 'datetime', 'price', 'shares', 'fee')

    def clean(self):
        cleaned_data = super().clean()
        self.check_duplicate_txn(cleaned_data, SellTransaction)
        return cleaned_data


class DividendTxnCreateForm(TxnFormMixin, forms.ModelForm):

    class Meta:
        model = DividendTrasaction
        fields = ('security', 'datetime', 'value')

    def clean(self):
        cleaned_data = super().clean()
        self.check_duplicate_txn(cleaned_data, DividendTrasaction)
        return cleaned_data


class SplitTxnCreateForm(TxnFormMixin, forms.ModelForm):

    class Meta:
        model = SplitTransaction
        fields = ('security', 'datetime', 'ratio')

    def clean(self):
        cleaned_data = super().clean()
        self.check_duplicate_txn(cleaned_data, SplitTransaction)
        return cleaned_data
