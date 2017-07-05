from decimal import Decimal
import datetime as dt
import pandas as pd

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth.models import User

from .models import Portfolio, Holding
from transactions.models import Transaction
from securities.models import Security
from transactions.factories import transaction_factory
from .factories import PortfolioFactory, HoldingFactory
from securities.factories import SecurityFactory, SecInfoFactory
from quotes.factories import QuoteFactory
from transactions.factories import TransactionFactory
from quotes.factories import QuoteFactory
from exchangerates.factories import ExchangeRateFactory


class PortfolioModelTest(TestCase):

    def setUp(self):
        # self.p1 = Portfolio.objects.create(name='value', description='testing')
        self.p1 = PortfolioFactory()
        self.s1 = SecurityFactory()
        self.s2 = SecurityFactory()
        self.s3 = SecurityFactory(currency='USD')

    def test_str(self):
        self.assertEqual(str(self.p1), self.p1.name)

    def test_absolute_url(self):
        self.assertEqual(self.p1.get_absolute_url(), reverse('portfolios:detail', args=[self.p1.id]))

    def test_reject_duplicated_name(self):
        with self.assertRaises(IntegrityError):
            PortfolioFactory(name=self.p1.name, description='another value', owner=self.p1.owner)

    def test_all_transactions(self):
        p2 = PortfolioFactory(name='trend', description='trending', owner=self.p1.owner)
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
        days = pd.bdate_range(start='2016-01-01', periods=5, freq='B')
        transaction_factory('buy', self.p1, self.s1, days[0], price=10, shares=200, fee=100)
        transaction_factory('sell', self.p1, self.s1, days[1], price=8, shares=100, fee=50)
        transaction_factory('dividend', self.p1, self.s1, days[2], dividend=35)
        transaction_factory('split', self.p1, self.s1, days[3], ratio=1.5)
        transaction_factory('sell', self.p1, self.s1, days[4], price=12, shares=100, fee=90)

        self.p1.update_holdings(days[-1]+1)

        hlds = list(Holding.objects.all())

        self.assertEqual(len(hlds), 5)
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

    def test_update_holdings_for_2_security(self):
        days = pd.bdate_range(start='2016-08-01', periods=3)
        transaction_factory('buy', self.p1, self.s1, days[0], price=10., shares=200, fee=100.)
        transaction_factory('sell', self.p1, self.s1, days[1], price=8., shares=100, fee=50.)
        transaction_factory('buy', self.p1, self.s2, days[1], price=80., shares=500, fee=120.)
        transaction_factory('sell', self.p1, self.s2, days[2], price=95, shares=200, fee=40.)

        self.p1.update_holdings(days[2])

        hld1 = list(Holding.objects.filter(security=self.s1).all())
        hld2 = list(Holding.objects.filter(security=self.s2).all())

        self.assertEqual(len(hld1), 2)
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
        self.assertEqual(len(hlds), 1)
        self.assertEqual(hlds[0].shares, 500)
        self.assertEqual(hlds[0].cost, -1000)
        self.assertEqual(hlds[0].date, dt.date(2016, 9, 6))

    # todo complete the following unit test
    def test_remove_holdings_after(self):
        pass

    def test_sum_each_currency(self):
        days = pd.bdate_range(start='2016-08-01', periods=3)
        transaction_factory('buy', self.p1, self.s1, days[0], price=10., shares=200, fee=100.)
        transaction_factory('sell', self.p1, self.s1, days[1], price=8., shares=100, fee=50.)
        transaction_factory('buy', self.p1, self.s3, days[1], price=80., shares=500, fee=120.)
        transaction_factory('sell', self.p1, self.s3, days[2], price=95, shares=200, fee=40.)
        QuoteFactory(security=self.s1, date=days[2], close=12.)
        QuoteFactory(security=self.s3, date=days[2], close=15.)

        self.p1.update_holdings(days[2])

        values = self.p1.sum_each_currency(days[2])
        self.assertAlmostEqual(values['CNY'], 1200)
        self.assertAlmostEqual(values['USD'], 4500)

    def test_sum_currency_as_l(self):
        pass

    def test_position_on_date_wo_transaction(self):
        days = pd.bdate_range(start='2016-08-01', periods=3)
        transaction_factory('buy', self.p1, self.s1, days[0], price=10., shares=200, fee=100.)
        transaction_factory('sell', self.p1, self.s1, days[1], price=8., shares=100, fee=50.)
        transaction_factory('buy', self.p1, self.s2, days[1], price=80., shares=500, fee=120.)
        transaction_factory('sell', self.p1, self.s2, days[2], price=95, shares=200, fee=40.)
        QuoteFactory(security=self.s1, date=days[2], close=12.)
        QuoteFactory(security=self.s2, date=days[2], close=15.)

        self.p1.update_holdings(days[2])

        hlds = self.p1.position(days[2])
        self.assertEqual(len(hlds), 2)
        self.assertAlmostEqual(self.p1.total_value(), 5700)

    def test_cash_flow(self):
        days = pd.bdate_range(start='2016-08-01', periods=4)
        transaction_factory('buy', self.p1, self.s1, days[0], price=10., shares=200, fee=100.)
        transaction_factory('sell', self.p1, self.s1, days[1], price=8., shares=100, fee=50.)
        transaction_factory('buy', self.p1, self.s2, days[1], price=80., shares=500, fee=120.)
        transaction_factory('sell', self.p1, self.s2, days[2], price=95, shares=200, fee=40.)
        QuoteFactory(security=self.s1, date=days[2], close=12.)
        QuoteFactory(security=self.s2, date=days[2], close=15.)

        self.assertEqual(self.p1.cash_flow(days[0]), -2100)
        self.assertEqual(self.p1.cash_flow(days[1]), -39370)
        self.assertEqual(self.p1.cash_flow(days[2]), 18960)
        self.assertEqual(self.p1.cash_flow(days[3]), 0)


# todo implement unit tests for Holding model
class HoldingModelTest(TestCase):

    def setUp(self):
        p1 = PortfolioFactory(name='value')
        s1 = SecurityFactory(symbol='MSYH')
        SecInfoFactory(security=s1, name='民生银行')
        self.hld = HoldingFactory(portfolio=p1, security=s1, shares=1000, cost=-15000, date=dt.date(2016, 1, 1))

    def tearDown(self):
        self.hld.delete()

    def test_str(self):
        self.assertEqual(str(self.hld), "@2016-01-01:value has 民生银行(MSYH):shares=1000,cost=-15000.00,"
                                        "value=0.00,dividend=0.00,gain=0.00")

    def test_cost_per_share_proper_value(self):
        self.assertEqual(self.hld.cost_per_share(), Decimal(15.0))

    def test_cost_per_share_zero_share(self):
        self.hld.shares = 0
        self.assertEqual(self.hld.cost_per_share(), Decimal(0))

    def test_as_table(self):
        self.hld.dividend = 25.
        self.hld.gain = 120.
        QuoteFactory(security=self.hld.security, date=self.hld.date, close=22.)
        self.hld.update_value()
        self.assertHTMLEqual(self.hld.as_t(), "<td><a href={sec_link}>民生银行</a></td>"
                                              "<td>MSYH</td><td>CNY</td><td>1000</td>"
                                              "<td>-15000.00</td><td>15.00</td><td>22000.00</td>"
                                              "<td>25.00</td><td>120.00</td>".format(
            sec_link=reverse('securities:detail', args=[self.hld.security.id])))

    def test_update_value(self):
        pass

    def test_update_all_values(self):
        pass


class PositionTest(TestCase):

    def setUp(self):
        self.p1 = PortfolioFactory(name='value')
        self.s1 = SecurityFactory(symbol='MSYH')
        self.s2 = SecurityFactory(symbol='GOOG', currency='USD')
        self.s3 = SecurityFactory(symbol='GLDQ')
        days = pd.bdate_range(start='2016-08-01', periods=3)
        self.days = days
        TransactionFactory(type='buy', portfolio=self.p1, security=self.s1, datetime=days[0], shares=100, price=5)
        TransactionFactory(type='buy', portfolio=self.p1, security=self.s2, datetime=days[1], shares=200)
        QuoteFactory(security=self.s1, date=days[0], close=10)
        QuoteFactory(security=self.s1, date=days[1], close=11)
        QuoteFactory(security=self.s1, date=days[2], close=12)
        QuoteFactory(security=self.s2, date=days[0], close=5)
        QuoteFactory(security=self.s2, date=days[1], close=7)
        QuoteFactory(security=self.s2, date=days[2], close=9)
        QuoteFactory(security=self.s3, date=days[0], close=20)
        QuoteFactory(security=self.s3, date=days[1], close=25)
        QuoteFactory(security=self.s3, date=days[2], close=30)
        ExchangeRateFactory(currency='USD', rate=Decimal(1.2), date=days[1])
        self.p1.update_holdings(days[2])

    def test_position_total_value_one_security(self):
        pos = self.p1.position(self.days[0])
        self.assertEqual(pos.total_value(), 1000)

    def test_position_value_two_securities_diff_currency(self):
        pos = self.p1.position(self.days[1])
        self.assertEqual(pos.value('CNY'), 1100)
        self.assertEqual(pos.value('USD'), 1400)

    def test_position_value_two_securities_same_currency(self):
        TransactionFactory(type='buy', portfolio=self.p1, security=self.s3, datetime=self.days[0], shares=30)
        self.p1.update_holdings(self.days[2])

        pos = self.p1.position(self.days[0])
        self.assertEqual(pos.value('CNY'), 1600)
        self.assertEqual(pos.total_value(), 1600)

    def test_position_total_value_two_sec_diff_currency(self):
        pos = self.p1.position(self.days[1])
        self.assertAlmostEqual(pos.total_value(), 2780)

    def test_portfolio_total_value(self):
        self.assertEqual(self.p1.total_value(self.days[0]), 1000)
        self.assertAlmostEqual(self.p1.total_value(self.days[1]), 2780)


class PortfolioReturnTest(TestCase):

    def setUp(self):
        self.p1 = PortfolioFactory(name='value')
        self.s1 = SecurityFactory(symbol='MSYH')
        self.s2 = SecurityFactory(symbol='GOOG', currency='USD')
        self.s3 = SecurityFactory(symbol='GLDQ')
        days = pd.bdate_range(start='2016-08-01', periods=3, offset='D')
        self.days = days
        TransactionFactory(type='buy', portfolio=self.p1, security=self.s1, datetime=days[0], shares=100, price=5)
        QuoteFactory(security=self.s1, date=days[0], close=10)
        QuoteFactory(security=self.s1, date=days[1], close=10.1)
        QuoteFactory(security=self.s1, date=days[2], close=10.2)
        QuoteFactory(security=self.s2, date=days[0], close=5)
        QuoteFactory(security=self.s2, date=days[1], close=7)
        QuoteFactory(security=self.s2, date=days[2], close=9)
        QuoteFactory(security=self.s3, date=days[0], close=20)
        QuoteFactory(security=self.s3, date=days[1], close=25)
        QuoteFactory(security=self.s3, date=days[2], close=30)
        ExchangeRateFactory(currency='USD', rate=Decimal(1.2), date=days[1])
        self.p1.update_holdings(days[2])

    def test_twrr_single_transaction_no_annualize(self):
        self.p1.update_performance()
        self.assertAlmostEqual(self.p1.twrr(start=self.days[0], end=self.days[2], annualize=False),
                               Decimal(0.02))

    def test_twrr_single_transaction_annualize(self):
        self.p1.update_performance()
        self.assertAlmostEqual(self.p1.twrr(start=self.days[0], end=self.days[2], annualize=True),
                               Decimal(1.02**(261/2)-1))

    def test_twrr_multiple_transactions(self):
        pass

    def test_mwrr_no_transaction_no_annualize(self):
        self.p1.update_performance()
        # note the transaction happens on days[0] while portfolio at the end of days[0] is used
        # as initial cost.
        self.assertAlmostEqual(self.p1.mwrr(start=self.days[0], end=self.days[2], annualize=False),
                               Decimal(0.02))

    def test_mwrr_single_transaction_no_annualize(self):
        self.p1.update_performance()
        self.assertAlmostEqual(self.p1.mwrr(start=self.days[0]-1, end=self.days[2], annualize=False),
                               Decimal(1.04))

    def test_performance_summary(self):
        pass