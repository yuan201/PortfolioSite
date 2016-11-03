from django.contrib import admin

from .models import Transaction
from core.mixins import AdminFormatMixin

@admin.register(Transaction)
class TransactionAdmin(AdminFormatMixin, admin.ModelAdmin):
    list_display = ('type', 'datetime', 'security', 'name', 'shares', '_price', '_fee', '_dividend', '_ratio')
    ordering = ['-datetime']

    def name(self, obj):
        return obj.security.name

    def _price(self, obj):
        return self._format_for_print(obj.price)

    def _fee(self, obj):
        return self._format_for_print(obj.fee)

    def _dividend(self, obj):
        return self._format_for_print(obj.dividend)

    def _ratio(self, obj):
        return self._format_for_print(obj.ratio)
