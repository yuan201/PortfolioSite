import datetime as dt

import tushare as ts

from django.core.management.base import BaseCommand

from securities.models import Security, SecurityInfo
from securities.forms import NewSecurityForm, NewSecurityInfoForm, UpdateSecurityListDateForm
import securities.models


class Command(BaseCommand):
    help = 'Get all securites and their basic infomations'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sec_added = 0
        self.info_added = 0

    def _add_or_get_security(self, symbol):
        try:
            return Security.objects.get(symbol=symbol)
        except securities.models.Security.DoesNotExist as e:
            form = NewSecurityForm({'symbol': symbol,
                                    'currency': 'CNY',
                                    'isindex': False,
                                    'list_date': ""})
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

    def _add_security_info(self, sec, info):
        data = {'security': sec.id,
                'valid_date': dt.date.today(),
                'name': info['name'],
                'industry': info['industry']}
        if sec.infos.count() > 0:
            form = NewSecurityInfoForm(data, last=sec.infos.latest())
        else:
            form = NewSecurityInfoForm(data)

        if form.is_valid():
            form.save()
            self.info_added += 1

    def _update_security_list_time(self, sec, date):
        data = {'list_date': date}
        form = UpdateSecurityListDateForm(data, instance=sec)
        if form.is_valid():
            form.save()

    def handle(self, *args, **options):
        self.stdout.write("Retrieving security basic info from Tushare")
        basics = ts.get_stock_basics()
        for symbol in basics.index:
            sec = self._add_or_get_security(symbol)
            info = basics.ix[symbol]
            self._add_security_info(sec, info)
            if self._md(info['timeToMarket']) and (not sec.list_date):
                self._update_security_list_time(sec, self._md(info['timeToMarket']))

        self.stdout.write(self.style.SUCCESS('Added {} Securities'.format(self.sec_added)))
        self.stdout.write(self.style.SUCCESS('Added {} Infos'.format(self.info_added)))
