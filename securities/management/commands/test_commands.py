from unittest.mock import MagicMock
import datetime as dt

from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO

import tushare as ts
import pandas as pd

from securities.models import Security, SecurityInfo
from securities.factories import SecurityFactory, SecInfoFactory


class GetBasicInfosTest(TestCase):

    def setUp(self):
        ts.get_stock_basics = MagicMock()
        ts.get_stock_basics.return_value = pd.DataFrame(
            data=[['SEC1', 'IND1', 1000, 500, 19970923]],
            columns=['name', 'industry', 'totals', 'outstanding', 'timeToMarket'],
            index=['600000'],
        )

    def test_command_empty_database_update_both_tables(self):
        call_command('getbasicinfos', 'Tushare')

        sec = Security.objects.first()
        self.assertEqual(Security.objects.count(), 1)
        self.assertEqual(sec.symbol, '600000')
        self.assertEqual(sec.infos.latest().name, 'SEC1')
        self.assertEqual(sec.infos.latest().industry, 'IND1')
        self.assertEqual(sec.infos.latest().valid_date, dt.date.today())
        self.assertEqual(sec.list_date, dt.date(1997, 9, 23))

    def test_command_console_output(self):
        out = StringIO()
        call_command('getbasicinfos', 'Tushare', stdout=out)

        self.assertIn('Added 1 Securities', out.getvalue())
        self.assertIn('Added 1 Infos', out.getvalue())

    def test_update_info_only_output(self):
        SecurityFactory(symbol='600000')

        out = StringIO()
        call_command('getbasicinfos', 'Tushare', stdout=out)

        self.assertIn('Added 0 Securities', out.getvalue())
        self.assertIn('Added 1 Infos', out.getvalue())

    def test_update_info_only_result(self):
        sec = SecurityFactory(symbol='600000')

        call_command('getbasicinfos', 'Tushare')

        self.assertEqual(sec.infos.latest().name, 'SEC1')

    def test_update_nothing_output(self):
        sec = SecurityFactory(symbol='600000')
        info = SecInfoFactory(security=sec, valid_date=dt.date.today(), name='NAME')

        out = StringIO()
        call_command('getbasicinfos', 'Tushare', stdout=out)

        self.assertIn('Added 0 Securities', out.getvalue())
        self.assertIn('Added 0 Securities', out.getvalue())

    def test_update_nothing_database(self):
        sec = SecurityFactory(symbol='600000')
        info = SecInfoFactory(security=sec, valid_date=dt.date.today(), name='NAME')

        call_command('getbasicinfos', 'Tushare')

        self.assertEqual(info.name, 'NAME')

    def test_add_another_info(self):
        sec = SecurityFactory(symbol='600000')
        info = SecInfoFactory(security=sec, valid_date=dt.date.today()-dt.timedelta(days=1), name='Old')

        call_command('getbasicinfos', 'Tushare')

        self.assertEqual(sec.infos.count(), 2)
        self.assertEqual(sec.infos.latest().name, 'SEC1')
