from django.contrib import admin

from .models import Quote


class QuoteAdmin(admin.ModelAdmin):
    list_display = ('security', 'date', '_open', '_close', '_high', '_low', '_volume')
    ordering = ['security', '-date']

    def _open(self, obj):
        return '{:.2f}'.format(obj.open)

    def _close(self, obj):
        return '{:.2f}'.format(obj.close)

    def _high(self, obj):
        return '{:.2f}'.format(obj.high)

    def _low(self, obj):
        return '{:.2f}'.format(obj.low)

    def _volume(self, obj):
        return '{:.2f}'.format(obj.volume)

admin.site.register(Quote, QuoteAdmin)