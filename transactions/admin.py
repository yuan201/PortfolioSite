from django.contrib import admin

from .models import BuyTransaction, SellTransaction, DividendTransaction, SplitTransaction

admin.site.register(BuyTransaction)
admin.site.register(SellTransaction)
admin.site.register(DividendTransaction)
admin.site.register(SplitTransaction)