import datetime as dt

from django.core.urlresolvers import reverse
from django.test import TestCase
import pandas as pd
from django.db.utils import IntegrityError
from django.contrib.auth.models import User

from .models import Portfolio, Holding
from transactions.models import Transaction
from securities.models import Security
from transactions.factories import transaction_factory
from .factories import PortfolioFactory
from securities.factories import SecurityFactory


class PortfolioModelTest(TestCase):

    def setUp(self):
        # self.p1 = Portfolio.objects.create(name='value', description='testing')
        self.p1 = PortfolioFactory()
        self.s1 = SecurityFactory()
        self.s2 = SecurityFactory()

    def test_str(self):
        self.assertEqual(str(self.p1), self.p1.name)

    def test_absolute_url(self):
        self.assertEqual(self.p1.get_absolute_url(), reverse('portfolios:detail', args=[self.p1.id]))

    def test_reject_duplicated_name(self):
        with self.assertRaises(IntegrityError):
            Portfolio.objects.create(name=self.p1.name, description='another value', owner=self.p1.owner)

    def test_all_transactions(self):
        p2 = Portfolio.objects.create(name='trend', description='trending', owner=self.p1.owner)
        _dt = [
            dt.datetime(2016, 1, 1, 11, 20),
            dt.datetime(2016, 1, 10, 14, 10),
            dt.datetime(2016, 1, 6, 9, 40),
            dt.datetime(2016, 1, 3, 13, 5),
        ]
        s1 = [
            transaction_factory('buy', self.p1, self.s1, _dt[0], price=1, shares=100),
            transaction_factory('sell', self.p1, self.s1, _dt[1], price=1, shares=50),
            transaction_factory('split', self.p1, self.s1, _dt[2], ratio=1.5),
            transaction_factory('dividend', self.p1, self.s1, _dt[3], dividend=10),
        ]
        s2 = [
            transaction_factory('buy', p2, self.s1, _dt[0], price=2, shares=200),
            transaction_factory('sell', p2, self.s1, _dt[1], price=2, shares=100),
            transaction_factory('split', p2, self.s1, _dt[2], ratio=2),
            transaction_factory('dividend', p2, self.s1, _dt[3], dividend=50),
        ]

        all_txn = self.p1.transactions.all()

        # test only p1 transactions are included
        for s in s1:
            self.assertIn(s, all_txn)
        for s in s2:
            self.assertNotIn(s, all_txn)

        # test the transaction array is properly sorted according to datetime
        self.assertEqual(all_txn[0].datetime, _dt[0])
        self.assertEqual(all_txn[1].datetime, _dt[3])
        self.assertEqual(all_txn[2].datetime, _dt[2])
        self.assertEqual(all_txn[3].datetime, _dt[1])

    def test_update_holdings(self):
        days = pd.bdate_range(start='2016-01-01', periods=5)
        transaction_factory('buy', self.p1, self.s1, days[0], price=10, shares=200, fee=100)
        transaction_factory('sell', self.p1, self.s1, days[1], price=8, shares=100, fee=50)
        transaction_factory('dividend', self.p1, self.s1, days[2], dividend=35)
        transaction_factory('split', self.p1, self.s1, days[3], ratio=1.5)
        transaction_factory('sell', self.p1, self.s1, days[4], price=12, shares=100, fee=90)

        self.p1.update_holdings(days[4]+1)

        hlds = list(Holding.objects.all())

        self.assertEqual(len(hlds), 6)
        self.assertEqual(hlds[0].shares, 200)
        self.assertAlmostEqual(hlds[0].cost, -2100)
        self.assertEqual(hlds[0].gain, 0)
        self.assertEqual(hlds[0].dividend, 0)

        self.assertEqual(hlds[1].shares, 100)
        self.assertAlmostEqual(hlds[1].cost, -1050)
        self.assertAlmostEqual(hlds[1].gain, -300)
        self.assertEqual(hlds[1].dividend, 0)

        self.assertEqual(hlds[2].shares, 100)
        self.assertEqual(hlds[2].dividend, 35)

        self.assertEqual(hlds[3].shares, 150)
        self.assertAlmostEqual(hlds[3].cost, -1050)

        self.assertEqual(hlds[4].shares, 50)
        self.assertEqual(hlds[4].cost, -350)
        self.assertAlmostEqual(hlds[4].gain, 110)
        self.assertEqual(hlds[4].dividend, 35)

        self.assertEqual(hlds[5].shares, 50)

    def test_update_holdings_for_2_security(self):
        days = pd.bdate_range(start='2016-08-01', periods=3)
        transaction_factory('buy', self.p1, self.s1, days[0], price=10., shares=200, fee=100.)
        transaction_factory('sell', self.p1, self.s1, days[1], price=8., shares=100, fee=50.)
        transaction_factory('buy', self.p1, self.s2, days[1], price=80., shares=500, fee=120.)
        transaction_factory('sell', self.p1, self.s2, days[2], price=95, shares=200, fee=40.)

        self.p1.update_holdings(days[2])

        hld1 = list(Holding.objects.filter(security=self.s1).all())
        hld2 = list(Holding.objects.filter(security=self.s2).all())

        self.assertEqual(len(hld1), 3)
        self.assertEqual(len(hld2), 2)

    def test_update_with_old_transactions_no_update(self):
        day = pd.Timestamp(dt.date(2016, 1, 1), offset='B')
        t1 = transaction_factory('buy', self.p1, self.s1, day-1, price=10., shares=100, fee=5.)
        Holding.objects.create(security=self.s1, portfolio=self.p1, shares=500, cost=-1000, date=day)

        self.p1.update_holdings(day)

        self.assertEqual(Holding.objects.count(), 1)
        hld = Holding.objects.first()
        self.assertEqual(hld.shares, 500)
        self.assertEqual(hld.cost, -1000)
        self.assertEqual(hld.date, dt.date(2016, 1, 1))

    def test_update_with_old_transactions_update_one_day(self):
        day = pd.Timestamp(dt.date(2016, 9, 5), offset='B')
        t1 = transaction_factory('buy', self.p1, self.s1, day, price=10., shares=100, fee=5.)
        Holding.objects.create(security=self.s1, portfolio=self.p1, shares=500, cost=-1000, date=day+1)

        self.p1.update_holdings(day+2)

        hlds = list(Holding.objects.all())
        self.assertEqual(len(hlds), 2)
        self.assertEqual(hlds[0].shares, 500)
        self.assertEqual(hlds[0].cost, -1000)
        self.assertEqual(hlds[0].date, dt.date(2016, 9, 6))

        self.assertEqual(hlds[1].shares, 500)
        self.assertEqual(hlds[1].date, dt.date(2016, 9, 7))

    # todo complete the following unit test
    def test_remove_holdings_after(self):
        pass

    def test_sum_each_currency(self):
        pass

    def test_sum_currency_as_l(self):
        pass


# todo implement unit tests for Holding model
class HoldingModelTest(TestCase):

    def setUp(self):
        pass

    def test_str(self):
        pass

    def test_cost_per_share_proper_value(self):
        pass

    def test_cost_per_share_zero_share(self):
        pass

    def test_as_table(self):
        pass

    def test_update_value(self):
        pass

    def test_update_all_values(self):
        pass

