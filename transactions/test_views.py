from unittest import skip
import datetime as dt
from decimal import Decimal

from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import BuyTransaction, SellTransaction, DividendTrasaction
from .models import SplitTransaction, Holding, Security
from portfolio.models import Portfolio


class NewTransactionTestBase(TestCase):

    def setUp(self):
        self.s1 = Security.objects.create(name='Google', symbol='GOOG', currency='USD')
        self.s2 = Security.objects.create(name='Apple', symbol='APPL', currency='USD')
        self.p1 = Portfolio.objects.create(name='BigCap', description='Test')

    def setup_buy_transaction(self):
        txndt = dt.datetime.strptime("2015-01-01 15:00:00", "%Y-%m-%d %H:%M:%S")
        self.t1 = BuyTransaction.objects.create(
            security=self.s1, portfolio=self.p1, datetime=txndt,
            price=10., shares=100, fee=6.
        )

    def setup_sell_transaction(self):
        txndt = dt.datetime.strptime("2015-01-01 15:00:00", "%Y-%m-%d %H:%M:%S")
        self.t2 = SellTransaction.objects.create(
            security=self.s1, portfolio=self.p1, datetime=txndt,
            price=12., shares=50, fee=2.
        )


class BuyTransactionCreateViewTest(NewTransactionTestBase):

    def test_can_post_a_new_buy_txn(self):
        self.client.post(reverse('transactions:add_buy', args=[self.p1.id]), data={
            'security': '1',
            'datetime': '2015-1-1 15:00:00',
            'price': '15.3',
            'shares': '100',
            'fee': '10.1',
        })

        txn = BuyTransaction.objects.first()
        self.assertEqual(txn.security, self.s1)
        self.assertEqual(txn.portfolio, self.p1)
        self.assertEqual(txn.datetime, dt.datetime(2015, 1, 1, 15, 0, 0, tzinfo=dt.timezone.utc))
        self.assertAlmostEqual(txn.price, Decimal(15.3))
        self.assertEqual(txn.shares, Decimal(100))
        self.assertAlmostEqual(txn.fee, Decimal(10.1))

    def test_cannot_post_a_colliding_txn(self):
        self.setup_buy_transaction()

        response = self.client.post(reverse('transactions:add_buy', args=[self.p1.id]), data={
            'security': '1',
            'datetime': '2015-01-01 15:00:00',
            'price': '12.0',
            'shares': '200',
            'fee': '20.0',
        })

        self.assertFormError(response, 'form', None, "Transaction Already Exists")


class SellTransactionCreateViewTest(NewTransactionTestBase):

    def test_can_post_a_new_sell_txn(self):
        self.client.post(reverse('transactions:add_sell', args=[self.p1.id]), data={
            'security': '1',
            'datetime': '2015-7-6 9:30:00',
            'price': '26.2',
            'shares': '1000',
            'fee': '25.4'
        })

        txn = SellTransaction.objects.first()
        self.assertEqual(txn.security, self.s1)
        self.assertEqual(txn.portfolio, self.p1)
        self.assertEqual(txn.datetime, dt.datetime(2015, 7, 6, 9, 30, 0, tzinfo=dt.timezone.utc))
        self.assertAlmostEqual(txn.price, Decimal(26.2))
        self.assertEqual(txn.shares, Decimal(1000))
        self.assertAlmostEqual(txn.fee, Decimal(25.4))

