from django import forms

from .models import BuyTransaction, SellTransaction, DividendTrasaction, SplitTransaction


class BuyTxnCreateForm(forms.ModelForm):

    class Meta:
        model = BuyTransaction
        fields = ('security', 'datetime', 'price', 'shares', 'fee')



