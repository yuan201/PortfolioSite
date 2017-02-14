from django.contrib import admin

from .models import Quote
from core.mixins import AdminFormatMixin


@admin.register(Quote)
class QuoteAdmin(AdminFormatMixin, admin.ModelAdmin):
    list_display = ('security', 'date', '_open', '_close', '_high', '_low', '_volume')
    ordering = ['security', '-date']

    # TODO find a universal way to solve this formatting problem
    def _open(self, obj):
        return self._format_for_print(obj.open)

    def _close(self, obj):
        return self._format_for_print(obj.close)

    def _high(self, obj):
        return self._format_for_print(obj.high)

    def _low(self, obj):
        return self._format_for_print(obj.low)

    def _volume(self, obj):
        return self._format_for_print(obj.volume)

