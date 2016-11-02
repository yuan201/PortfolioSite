from django.contrib import admin

from .models import Quote


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('security', 'date', '_open', '_close', '_high', '_low', '_volume')
    ordering = ['security', '-date']

    @staticmethod
    def _format_for_print(value):
        return '{:.2f}'.format(value)

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

