import datetime as dt
import csv

import tushare as ts
import pandas as pd

from django.core.management.base import BaseCommand

from securities.models import Security, SecurityInfo
from securities.forms import NewSecurityForm, NewSecurityInfoForm, UpdateSecListDateForm, UpdateSecCurrencyForm, UpdateSecExchangeForm
import securities.models


class Command(BaseCommand):
    help = 'Get all securites and their basic infomations'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sec_added = 0
        self.info_added = 0

    def add_arguments(self, parser):
        parser.add_argument('source')
        parser.add_argument('--file', nargs=1)

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
                'name': info['name'].strip(),
                'industry': info['industry'].strip()}
        if sec.infos.count() > 0:
            form = NewSecurityInfoForm(data, last=sec.infos.latest())
        else:
            form = NewSecurityInfoForm(data)

        if form.is_valid():
            form.save()
            self.info_added += 1

    FIXED_FORMS = {
        'list_date': UpdateSecListDateForm,
        'currency': UpdateSecCurrencyForm,
        'exchange': UpdateSecExchangeForm,
    }

    @classmethod
    def _update_security_fixed_info(cls, sec, field, data):
        form = cls.FIXED_FORMS[field]({field: data}, instance=sec)
        if form.is_valid():
            form.save()

    @staticmethod
    def _convert_csv_to_dataframe(csvfile):
        basics = pd.read_csv(csvfile, dtype=str)
        basics = basics.set_index('symbol')
        return basics

    @classmethod
    def _update_fixed_infos(cls, sec, info):
        for f in "list_date currency exchange".split():
            if f in info and info[f]:
                cls._update_security_fixed_info(sec, f, info[f])

    def _update_database(self, basics):
        for symbol in basics.index:
            sec = self._add_or_get_security(symbol)
            info = basics.ix[symbol]
            self._add_security_info(sec, info)
            self._update_fixed_infos(sec, info)

    def handle(self, *args, **options):
        self.stdout.write("Updating security basic infomation")
        source = options['source']
        if options['source'] == 'Tushare':
            basics = ts.get_stock_basics()
            basics = basics.rename(columns={'timeToMarket': 'list_date'})
            basics['list_date'] = basics['list_date'].map(self._md)
        elif options['source'] == 'Local':
            basics = self._convert_csv_to_dataframe(options['file'][0])
        else:
            self.stdout.write("Wrong Source")
            return

        self._update_database(basics)

        self.stdout.write(self.style.SUCCESS('Added {} Securities'.format(self.sec_added)))
        self.stdout.write(self.style.SUCCESS('Added {} Infos'.format(self.info_added)))
