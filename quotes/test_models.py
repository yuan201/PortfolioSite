import logging
from decimal import Decimal
import datetime as dt

from django.test import TestCase
import pandas as pd
import numpy as np

from .models import Quote
from securities.models import Security
from securities.factories import SecurityFactory
from .factories import QuoteFactory


logger = logging.getLogger(__name__)


class QuoteModelTest(TestCase):
    def setUp(self):
        self.df = pd.DataFrame(np.random.random(25).reshape(5, 5),
                               index=pd.date_range('2016-01-01', periods=5, freq='D'),
                               columns=['open', 'close', 'high', 'low', 'volume'])
        # self.s1 = Security.objects.create(name='民生银行', symbol='MSYH', currency='RMB')
        self.s1 = SecurityFactory()

    def test_add_quotes(self):
        Quote.add_quotes(self.df, self.s1)

        q1 = Quote.objects.first()
        self.assertEqual(q1.security, self.s1)
        self.assertEqual(Quote.objects.count(), 5)

    def test_to_dataframe(self):
        Quote.add_quotes(self.df, self.s1)

        df_new = Quote.to_DataFrame(Quote.objects.all())
        # logger.debug("df_new={}".format(df_new))
        # logger.debug("df={}".format(self.df))
        # logger.debug("compare:{}".format(df_new.eq(self.df)))
        self.assertTrue(df_new.astype(float).eq(self.df.astype(float)).all().all())


class QuoteModelUpdateQuotesTest(TestCase):
    def setUp(self):
        self.s1 = Security.objects.create(symbol='MSYH', currency='RMB')
        self.q1 = Quote.objects.create(security=self.s1, date=dt.date(2016, 1, 1), open=10.,
                                       close=11., high=12., low=9., volume=100.)
        self.q2 = Quote.objects.create(security=self.s1, date=dt.date(2015, 12, 31), open=5.,
                                       close=6., high=7., low=4., volume=10.)
        self.df = pd.DataFrame([(100., 110., 120., 90., 1000.,), (50., 60., 70., 40., 100.,)],
                               index=pd.date_range('2016-01-01', periods=2, freq='D'),
                               columns=['open', 'close', 'high', 'low', 'volume'])

    def test_update_quotes_discard_existing_mode(self):
        Quote.update_quotes(self.df, self.s1, 'discard')

        self.assertEqual(Quote.objects.count(), 2)
        df_new = Quote.to_DataFrame(Quote.objects.all())
        self.assertTrue(df_new.astype(float).eq(self.df.astype(float)).all().all())

    def test_update_quotes_overwrite_mode(self):
        Quote.update_quotes(self.df, self.s1, 'overwrite')

        self.assertEqual(Quote.objects.count(), 3)
        df_new = Quote.to_DataFrame(Quote.objects.filter(date__gte=dt.date(2016, 1, 1)).all())
        # logger.debug("df_new={}".format(df_new))
        self.assertTrue(df_new.astype(float).eq(self.df.astype(float)).all().all())
        q = Quote.objects.filter(date=dt.date(2015, 12, 31)).first()
        self.assertEqual(q, self.q2)

    def test_update_quotes_append_mode(self):
        Quote.update_quotes(self.df, self.s1, 'append')

        self.assertEqual(Quote.objects.count(), 3)
        q1_2 = Quote.objects.filter(date=dt.date(2016, 1, 2)).first()
        q1_1 = Quote.objects.filter(date=dt.date(2016, 1, 1)).first()
        q12_31 = Quote.objects.filter(date=dt.date(2015, 12, 31)).first()

        self.assertEqual(q1_1, self.q1)
        self.assertEqual(q12_31, self.q2)
        self.assertAlmostEqual(q1_2.open, 50.)
        self.assertAlmostEqual(q1_2.volume, 100.)

    def test_empty_df_discard_existing_mode(self):
        Quote.update_quotes(pd.DataFrame(), self.s1, 'discard')

        self.assertEqual(Quote.objects.count(), 0)

    def test_empty_df_overwrite_mode(self):
        Quote.update_quotes(pd.DataFrame(), self.s1, 'overwrite')

        self.assertEqual(Quote.objects.filter(date=dt.date(2016, 1, 1)).first(), self.q1)
        self.assertEqual(Quote.objects.filter(date=dt.date(2015, 12, 31)).first(), self.q2)

    def test_empty_df_append_mode(self):
        Quote.update_quotes(pd.DataFrame(), self.s1, 'append')

        self.assertEqual(Quote.objects.filter(date=dt.date(2016, 1, 1)).first(), self.q1)
        self.assertEqual(Quote.objects.filter(date=dt.date(2015, 12, 31)).first(), self.q2)

