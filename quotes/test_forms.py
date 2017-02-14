from unittest.mock import patch

from django.test import TestCase
import pandas as pd
import numpy as np

from .forms import QuotesForm
from securities.models import Security
from securities.factories import SecurityFactory
from quoters.quoter import Quoter, SymbolNotExist
from quotes.models import Quote


class QuotesFormTest(TestCase):

    # todo try factory_boy to build test records
    def setUp(self):
        self.s1 = SecurityFactory(symbol='MSYH', currency='RMB', exchange='SSE')
        self.data = {'start': '2016-01-01', 'end': '2016-01-10', 'mode': 'overwrite', 'quoter': 'Tushare'}

    def test_error_on_wrong_date(self):
        data = {'start': '2016-01-01', 'end': '2015-12-31', 'mode': 'overwrite', 'quoter': 'Tushare'}
        form = QuotesForm(data, security=self.s1)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['start'],["end date before start date"])

    def test_error_on_empty_exchange(self):
        self.s1.exchange = None
        form = QuotesForm(self.data, security=self.s1)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], ["Exchange not specified"])

    @patch('quoters.quotertushare.QuoterTushare.get_quotes')
    def test_error_on_wrong_symbol(self, mock_quoter):
        mock_quoter.side_effect = SymbolNotExist()
        form = QuotesForm(self.data, security=self.s1)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], ["symbol not found on this quoter"])

    @patch('quoters.quotertushare.QuoterTushare.get_quotes')
    def test_save_quotes_to_db(self, mock_quoter):
        mock_quoter.return_value = pd.DataFrame(np.random.random(25).reshape(5, 5),
                                                index=pd.date_range('2016-01-01', periods=5, freq='D'),
                                                columns=['open', 'close', 'high', 'low', 'volume'])
        self.s1.quoter = "Tushare"
        data = {'start': '2016-01-01', 'end': '2016-01-10', 'mode': 'discard', 'quoter': 'Tushare'}
        form = QuotesForm(data, security=self.s1)

        self.assertTrue(form.is_valid())

        form.save_quotes()
        q1 = Quote.objects.first()
        self.assertEqual(Quote.objects.count(), 5)
        self.assertEqual(q1.security, self.s1)
