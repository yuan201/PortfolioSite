import datetime as dt
import pandas as pd

from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import Security
from quotes.models import Quote


class SecurityModelTest(TestCase):

    # todo use factory_boy to generate test quote
    @staticmethod
    def create_quote(security, date, close):
        return Quote.objects.create(security=security, date=date, high=close+0.5, low=close-1.5,
                                    open=close-1.0, close=close, volume=close*100)

    def setUp(self):
        self.s1 = Security.objects.create(name="民生银行", symbol="MSYH", currency="RMB",
                                          quoter="Tushare", isindex=False)
        self.q1 = self.create_quote(self.s1, dt.date(2016, 9, 2), 10)
        self.s2 = Security.objects.create(name="格力电器", symbol="000651", currency="RMB",
                                          quoter="Tushare", isindex=False)

    def test_model_str(self):
        self.assertEqual(str(self.s1), "{}({})".format(self.s1.name, self.s1.symbol))

    def test_model_as_t_with_quote(self):
        self.assertHTMLEqual(self.s1.as_t(),
                             "<td><a href={link}>{symbol}</a></td><td>{name}</td> \
                          <td>{currency}</td><td>1</td><td>10.00</td>".format(
                                 link=self.s1.get_absolute_url(), symbol=self.s1.symbol,
                                 name=self.s1.name, currency=self.s1.currency)
                             )

    def test_model_as_t_without_quote(self):
        self.assertHTMLEqual(self.s2.as_t(),
                             "<td><a href={link}>{symbol}</a></td><td>{name}</td> \
                          <td>{currency}</td><td>0</td><td></td>".format(
                                 link=self.s2.get_absolute_url(), symbol=self.s2.symbol,
                                 name=self.s2.name, currency=self.s2.currency)
                             )

    def test_absolute_url(self):
        self.assertEqual(self.s1.get_absolute_url(), reverse('securities:detail', args=[self.s1.id]))

    def test_quote_with_quote_on_the_date(self):
        self.assertAlmostEqual(self.s1.first_quote_before(self.q1.date), self.q1)

    def test_quote_with_quote_before_the_date(self):
        self.assertAlmostEqual(self.s1.first_quote_before(dt.date(2016, 9, 3)), self.q1)

    def test_quote_without_quote_return_none(self):
        self.assertIsNone(self.s1.first_quote_before(dt.date(2016, 9, 1)))

    def test_quote_between(self):
        start = dt.date(2016, 9, 1)
        end = dt.date(2016, 9, 5)
        self.create_quote(self.s2, dt.date(2016, 8, 31), 10.)
        self.create_quote(self.s2, dt.date(2016, 9, 2), 12.)

        quotes = self.s2.quotes_between(start, end)
        self.assertEqual(len(quotes), 3)
        self.assertTrue((quotes.index == pd.bdate_range(start, end)).all())
        self.assertAlmostEqual(quotes.ix['2016-09-01']['close'], 10.)
        self.assertAlmostEqual(quotes.ix['2016-09-02']['close'], 12.)
        self.assertAlmostEqual(quotes.ix['2016-09-05']['close'], 12.)
