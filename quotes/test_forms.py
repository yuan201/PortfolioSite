from unittest.mock import patch

from django.test import TestCase
import pandas as pd
import numpy as np

from .forms import QuotesForm
from securities.models import Security
from quoters.quoter import QuoterTushare, SymbolNotExist
from quotes.models import Quote


class QuotesFormTest(TestCase):

    def setUp(self):
        self.s1 = Security.objects.create(name='民生银行', symbol='MSYH', currency='RMB')
        self.data = {'start': '2016-01-01', 'end': '2016-01-10', 'mode': '2'}

    def test_error_on_wrong_date(self):
        data = {'start': '2016-01-01', 'end': '2015-12-31', 'mode': '2'}
        form = QuotesForm(data, security=self.s1)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['start'],["end date before start date"])

    def test_error_on_empty_quoter(self):
        form = QuotesForm(self.data, security=self.s1)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], ["Quoter not specified"])

    def test_error_on_wrong_quoter(self):
        self.s1.quoter = "Wrong"
        form = QuotesForm(self.data, security=self.s1)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], ["Unknown Quoter"])

    @patch('quoters.quoter.QuoterTushare.get_quotes')
    def test_error_on_wrong_symbol(self, mock_quoter):
        mock_quoter.side_effect = SymbolNotExist()
        self.s1.quoter = "Tushare"
        form = QuotesForm(self.data, security=self.s1)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], ["symbol not found on this quoter"])

    @patch('quoters.quoter.QuoterTushare.get_quotes')
    def test_save_quotes_to_db(self, mock_quoter):
        mock_quoter.return_value = pd.DataFrame(np.random.random(25).reshape(5, 5),
                                                index=pd.date_range('2016-01-01', periods=5, freq='D'),
                                                columns=['open', 'close', 'high', 'low', 'volume'])
        self.s1.quoter = "Tushare"
        data = {'start': '2016-01-01', 'end': '2016-01-10', 'mode': '3'}
        form = QuotesForm(data, security=self.s1)

        self.assertTrue(form.is_valid())

        form.save_quotes()
        q1 = Quote.objects.first()
        self.assertEqual(Quote.objects.count(), 5)
        self.assertEqual(q1.security, self.s1)
