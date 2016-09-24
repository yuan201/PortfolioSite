import datetime as dt

from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Portfolio, Holding
from transactions.models import BuyTransaction, SellMoreThanHold, SplitTransaction, DividendTransaction
from transactions.models import transaction_factory
from securities.models import Security


class PortfolioModelTest(TestCase):

    def setUp(self):
        self.p1 = Portfolio.objects.create(name='value', description='testing')
        self.s1 = Security.objects.create(name='民生银行', symbol='MSYH', currency='RMB')

    def test_str(self):
        self.assertEqual(str(self.p1), self.p1.name)

    def test_absolute_url(self):
        self.assertEqual(self.p1.get_absolute_url(), reverse('portfolios:detail', args=[self.p1.id]))

    def test_all_transactions(self):
        p2 = Portfolio.objects.create(name='trend', description='trending')
        _dt = dt.datetime(2016, 1, 1, 11, 20)
        s1 = []
        s2 = []
        s1.append(transaction_factory('buy', self.p1, self.s1, _dt, price=1, shares=100))
        s1.append(transaction_factory('sell', self.p1, self.s1, _dt, price=1, shares=50))
        s1.append(transaction_factory('split', self.p1, self.s1, _dt, ratio=1.5))
        s1.append(transaction_factory('dividend', self.p1, self.s1, _dt, dividend=10))
        s2.append(transaction_factory('buy', p2, self.s1, _dt, price=2, shares=200))
        s2.append(transaction_factory('sell', p2, self.s1, _dt, price=2, shares=100))
        s2.append(transaction_factory('split', p2, self.s1, _dt, ratio=2))
        s2.append(transaction_factory('dividend', p2, self.s1, _dt, dividend=50))

        all_txn = self.p1.transactions()

        for s in s1:
            self.assertIn(s, all_txn)
        for s in s2:
            self.assertNotIn(s, all_txn)

