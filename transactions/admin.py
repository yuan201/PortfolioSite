from django.contrib import admin

from .models import Security, BuyTransaction, SellTransaction, DividendTrasaction, SplitTransaction

admin.site.register(Security)
admin.site.register(BuyTransaction)
admin.site.register(SellTransaction)
admin.site.register(DividendTrasaction)
admin.site.register(SplitTransaction)