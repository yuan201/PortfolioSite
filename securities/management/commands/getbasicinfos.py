import datetime as dt

import tushare as ts

from django.core.management.base import BaseCommand, CommandError

from securities.models import Security, SecurityInfo
from securities.forms import NewSecurityForm, NewSecurityInfoForm
import securities.models


class Command(BaseCommand):
    help = 'Get all securites and their basic infomations'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sec_added = 0
        self.info_added = 0

    def add_or_get_security(self, symbol):
        try:
            return Security.objects.get(symbol=symbol)
        except securities.models.Security.DoesNotExist as e:
            form = NewSecurityForm({'symbol': symbol,
                                    'currency': 'CNY',
                                    'quoter': 'Tushare',
                                    'isindex': False})
            if form.is_valid():
                self.sec_added += 1
                return form.save()

    @staticmethod
    def _md(td):
        """convert date from tushare yyyymmdd to yyyy-mm-dd"""
        td = str(td)
        if len(td) == 8:
            return td[0:4] + '-' + td[4:6] + '-' + td[6:]
        return ""

    def handle(self, *args, **options):
        self.stdout.write("Retrieving security basic info from Tushare")
        basics = ts.get_stock_basics()
        for symbol in basics.index:
            sec = self.add_or_get_security(symbol)
            infos = basics.ix[symbol]
            form = NewSecurityInfoForm({'security': sec.id,
                                        'valid_date': dt.date.today(),
                                        'name': infos['name'],
                                        'industry': infos['industry'],
                                        'total_shares': infos['totals'],
                                        'outstanding_shares': infos['outstanding'],
                                        'list_date': self._md(infos['timeToMarket'])})
            if form.is_valid():
                self.info_added += 1
                form.save()

        self.stdout.write(self.style.SUCCESS('Added {} Securities'.format(self.sec_added)))
        self.stdout.write(self.style.SUCCESS('Added {} Infos'.format(self.info_added)))
