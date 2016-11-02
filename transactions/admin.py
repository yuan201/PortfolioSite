from django.contrib import admin

from .models import BuyTransaction, SellTransaction, DividendTransaction, SplitTransaction, Transaction2

admin.site.register(BuyTransaction)
admin.site.register(SellTransaction)
admin.site.register(DividendTransaction)
admin.site.register(SplitTransaction)
admin.site.register(Transaction2)