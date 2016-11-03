from unittest import skip
import datetime as dt
from decimal import Decimal

from django.test import TestCase
from django.core.urlresolvers import reverse
import factory

from .models import Transaction
from portfolios.models import Portfolio
from securities.models import Security
from portfolios.factories import PortfolioFactory
from securities.factories import SecurityFactory
from .factories import TransactionFactory


class NewUpdateTxnTestMixin(object):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        factory.create_batch(SecurityFactory, 2)
        PortfolioFactory()

    def setup_buy_transaction(self):
        txndt = dt.datetime(2015, 1, 1, 15, 0)
        s1, s2 = Security.objects.all()
        p1 = Portfolio.objects.first()
        self.buytxn = TransactionFactory(type='buy', security=s1, portfolio=p1, datetime=txndt,
                                         price=10., shares=100, fee=6)

    def setup_sell_transaction(self):
        txndt = dt.datetime(2015, 1, 2, 15, 10)
        s1, s2 = Security.objects.all()
        p1 = Portfolio.objects.first()
        self.selltxn = TransactionFactory(type='sell', security=s2, portfolio=p1,
                                          datetime=txndt, price=12., shares=50, fee=2.)

    def setup_dividend_transaction(self):
        txndt = dt.datetime(2015, 3, 1, 9, 45, 0)
        s1, s2 = Security.objects.all()
        p1 = Portfolio.objects.first()
        self.divtxn = TransactionFactory(type='dividend', security=s1, portfolio=p1,
                                         datetime=txndt, dividend=45.8)


class BuyTxnCreateViewTest(NewUpdateTxnTestMixin, TestCase):

    def test_can_post_a_new_buy_txn(self):
        s1, s2 = Security.objects.all()
        p1 = Portfolio.objects.first()
        self.client.post(reverse('transactions:add', args=[p1.id]), data={
            'type': 'buy',
            'security': '{}'.format(s1.id),
            'datetime': '2015-1-1 15:00:00',
            'price': '15.3',
            'shares': '100',
            'fee': '10.1',
        })

        txn = Transaction.objects.first()
        self.assertEqual(txn.security, s1)
        self.assertEqual(txn.portfolio, p1)
        self.assertEqual(txn.datetime, dt.datetime(2015, 1, 1, 15, 0, 0))
        self.assertAlmostEqual(txn.price, Decimal(15.3))
        self.assertEqual(txn.shares, Decimal(100))
        self.assertAlmostEqual(txn.fee, Decimal(10.1))

    def test_cannot_post_a_colliding_txn(self):
        s1, s2 = Security.objects.all()
        p1 = Portfolio.objects.first()
        self.setup_buy_transaction()

        response = self.client.post(reverse('transactions:add', args=[p1.id]), data={
            'security': '{}'.format(s1.id),
            'type': 'buy',
            'datetime': '2015-01-01 15:00:00',
            'price': '12.0',
            'shares': '200',
            'fee': '20.0',
        })

        self.assertFormError(response, 'form', None, "Transaction Already Exists")


class SellTxnCreateViewTest(NewUpdateTxnTestMixin, TestCase):

    def test_can_post_a_new_sell_txn(self):
        s1, s2 = Security.objects.all()
        p1 = Portfolio.objects.first()

        self.client.post(reverse('transactions:add', args=[p1.id]), data={
            'security': '{}'.format(s1.id),
            'type': 'sell',
            'datetime': '2015-7-6 9:30:00',
            'price': '26.2',
            'shares': '1000',
            'fee': '25.4'
        })

        txn = Transaction.objects.first()
        self.assertEqual(txn.security, s1)
        self.assertEqual(txn.portfolio, p1)
        self.assertEqual(txn.datetime, dt.datetime(2015, 7, 6, 9, 30, 0))
        self.assertAlmostEqual(txn.price, Decimal(26.2))
        self.assertEqual(txn.shares, Decimal(1000))
        self.assertAlmostEqual(txn.fee, Decimal(25.4))

    def test_can_NOT_post_a_colling_txn(self):
        s1, s2 = Security.objects.all()
        p1 = Portfolio.objects.first()
        self.setup_sell_transaction()

        response = self.client.post(reverse('transactions:add', args=[p1.id]), data={
            'security': '{}'.format(s2.id),
            'type': 'sell',
            'datetime': '2015-01-02 15:10:00',
            'price': '13.5',
            'shares': '300',
            'fee': '15.3',
        })

        self.assertFormError(response, 'form', None, "Transaction Already Exists")


class SplitTxnCreateViewTest(NewUpdateTxnTestMixin, TestCase):

    def test_can_post_a_new_split_txn(self):
        s1, s2 = Security.objects.all()
        p1 = Portfolio.objects.first()

        self.client.post(reverse('transactions:add', args=[p1.id]), data={
            'security': '{}'.format(s2.id),
            'type': 'split',
            'datetime': '2015-5-3 10:24:00',
            'ratio': '1.5',
        })

        txn = Transaction.objects.first()
        self.assertEqual(txn.security, s2)
        self.assertEqual(txn.portfolio, p1)
        self.assertEqual(txn.datetime, dt.datetime(2015, 5, 3, 10, 24, 0))
        self.assertAlmostEqual(txn.ratio, Decimal(1.5))


class DividendTxnCreateViewTest(NewUpdateTxnTestMixin, TestCase):

    def test_can_post_a_new_dividend_txn(self):
        s1, s2 = Security.objects.all()
        p1 = Portfolio.objects.first()

        self.client.post(reverse('transactions:add', args=[p1.id]), data={
            'security': '{}'.format(s2.id),
            'type': 'dividend',
            'datetime': '2015-3-2 11:30:00',
             'dividend': '120',
        })

        txn = Transaction.objects.first()
        self.assertEqual(txn.security, s2)
        self.assertEqual(txn.portfolio, p1)
        self.assertEqual(txn.datetime, dt.datetime(2015, 3, 2, 11, 30, 0))
        self.assertAlmostEqual(txn.dividend, Decimal(120.))


class BuyTransactionUpdateViewTest(NewUpdateTxnTestMixin, TestCase):

    def test_can_update_buy_txn(self):
        s1, s2 = Security.objects.all()
        self.setup_buy_transaction()

        self.client.post(reverse('transactions:update', args=[self.buytxn.id]), data={
            'security': '{}'.format(s1.id),
            'type': 'buy',
            'datetime': '2015-02-01 15:00:00',
            'price': '16.2',
            'shares': '200',
            'fee': '21.2',
        })

        txn = Transaction.objects.first()
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertAlmostEqual(txn.price, Decimal(16.2))
        self.assertAlmostEqual(txn.shares, Decimal(200))
        self.assertAlmostEqual(txn.fee, Decimal(21.2))
        self.assertEqual(txn.datetime, dt.datetime(2015, 2, 1, 15, 0, 0))


class SellTransactionUpdateViewTest(NewUpdateTxnTestMixin, TestCase):

    def test_can_update_sell_txn(self):
        s1, s2 = Security.objects.all()
        self.setup_sell_transaction()

        self.client.post(reverse('transactions:update', args=[self.selltxn.id]), data={
            'security': '{}'.format(s1.id),
            'type': 'sell',
            'datetime': '2015-02-02 14:20:00',
            'price': '14.3',
            'shares': '100',
            'fee': '5.2',
        })

        txn = Transaction.objects.first()
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(txn.security, s1)
        self.assertEqual(txn.datetime, dt.datetime(2015, 2, 2, 14, 20, 0))
        self.assertAlmostEqual(txn.price, Decimal(14.3))
        self.assertAlmostEqual(txn.shares, Decimal(100))
        self.assertAlmostEqual(txn.fee, Decimal(5.2))


class DividendTransactionUpdateViewTest(NewUpdateTxnTestMixin, TestCase):

    def test_can_update_dividend_txn(self):
        s1, s2 = Security.objects.all()
        self.setup_dividend_transaction()

        self.client.post(reverse('transactions:update', args=[self.divtxn.id]), data={
            'security': '{}'.format(s2.id),
            'type': 'dividend',
            'datetime': '2015-4-5 10:21:10',
            'dividend': '98.2',
        })

        txn = Transaction.objects.first()
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(txn.security, s2)
        self.assertEqual(txn.datetime, dt.datetime(2015, 4, 5, 10, 21, 10))
        self.assertAlmostEqual(txn.dividend, Decimal(98.2))

