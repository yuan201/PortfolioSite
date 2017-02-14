from django.contrib import admin

from .models import ExchangeRate
from core.mixins import AdminFormatMixin


@admin.register(ExchangeRate)
class ExchangeRateAdmin(AdminFormatMixin, admin.ModelAdmin):
    list_display = ('date', 'currency', '_rate')
    ordering = ['-date']

    def _rate(self, obj):
        return self._format_for_print(obj.rate)
