from unittest import skip
import datetime as dt
from decimal import Decimal

from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import BuyTransaction, SellTransaction, DividendTrasaction
from .models import SplitTransaction, Holding, Security
from portfolio.models import Portfolio


class NewTransactionTestBase(TestCase):

    @classmethod
    def setUpClass(cls):
        super(NewTransactionTestBase, cls).setUpClass()
        Security.objects.create(name='Google', symbol='GOOG', currency='USD')
        Security.objects.create(name='Apple', symbol='APPL', currency='USD')
        Portfolio.objects.create(name='BigCap', description='Test')

    @classmethod
    def tearDownClass(cls):
        Security.objects.all().delete()
        Portfolio.objects.all().delete()
        super(NewTransactionTestBase, cls).tearDownClass()

    def setup_buy_transaction(self):
        txndt = dt.datetime.strptime("2015-01-01 15:00:00", "%Y-%m-%d %H:%M:%S")
        s1, s2 = Security.objects.all()
        p1 = Portfolio.objects.first()
        self.t1 = BuyTransaction.objects.create(
            security=s1, portfolio=p1, datetime=txndt,
            price=10., shares=100, fee=6.
        )

    def setup_sell_transaction(self):
        txndt = dt.datetime.strptime("2015-01-01 15:10:00", "%Y-%m-%d %H:%M:%S")
        s1, s2 = Security.objects.all()
        p1 = Portfolio.objects.first()
        self.t2 = SellTransaction.objects.create(
            security=s2, portfolio=p1, datetime=txndt,
            price=12., shares=50, fee=2.
        )


class BuyTransactionCreateViewTest(NewTransactionTestBase):

    def test_can_post_a_new_buy_txn(self):
        s1, s2 = Security.objects.all()
        p1 = Portfolio.objects.first()
        self.client.post(reverse('transactions:add_buy', args=[p1.id]), data={
            'security': '{}'.format(s1.id),
            'datetime': '2015-1-1 15:00:00',
            'price': '15.3',
            'shares': '100',
            'fee': '10.1',
        })

        txn = BuyTransaction.objects.first()
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

        response = self.client.post(reverse('transactions:add_buy', args=[p1.id]), data={
            'security': '{}'.format(s1.id),
            'datetime': '2015-01-01 15:00:00',
            'price': '12.0',
            'shares': '200',
            'fee': '20.0',
        })

        self.assertFormError(response, 'form', None, "Transaction Already Exists")


class SellTransactionCreateViewTest(NewTransactionTestBase):

    def test_can_post_a_new_sell_txn(self):
        s1, s2 = Security.objects.all()
        p1 = Portfolio.objects.first()

        self.client.post(reverse('transactions:add_sell', args=[p1.id]), data={
            'security': '{}'.format(s1.id),
            'datetime': '2015-7-6 9:30:00',
            'price': '26.2',
            'shares': '1000',
            'fee': '25.4'
        })

        txn = SellTransaction.objects.first()
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

        response = self.client.post(reverse('transactions:add_sell', args=[p1.id]), data={
            'security': '{}'.format(s2.id),
            'datetime': '2015-01-01 15:10:00',
            'price': '13.5',
            'shares': '300',
            'fee': '15.3',
        })

        self.assertFormError(response, 'form', None, "Transaction Already Exists")


class SplitTransactionCreateViewTest(NewTransactionTestBase):

    def test_can_post_a_new_split_txn(self):
        s1, s2 = Security.objects.all()
        p1 = Portfolio.objects.first()

        self.client.post(reverse('transactions:add_split', args=[p1.id]), data={
            'security': '{}'.format(s2.id),
            'datetime': '2015-5-3 10:24:00',
            'ratio': '1.5',
        })

        txn = SplitTransaction.objects.first()
        self.assertEqual(txn.security, s2)
        self.assertEqual(txn.portfolio, p1)
        self.assertEqual(txn.datetime, dt.datetime(2015, 5, 3, 10, 24, 0))
        self.assertAlmostEqual(txn.ratio, Decimal(1.5))


class DividendTransactionCreateViewTest(NewTransactionTestBase):

    def test_can_post_a_new_dividend_txn(self):
        s1, s2 = Security.objects.all()
        p1 = Portfolio.objects.first()

        self.client.post(reverse('transactions:add_dividend', args=[p1.id]), data={
            'security': '{}'.format(s2.id),
            'datetime': '2015-3-2 11:30:00',
            'value': '120',
        })

        txn = DividendTrasaction.objects.first()
        self.assertEqual(txn.security, s2)
        self.assertEqual(txn.portfolio, p1)
        self.assertEqual(txn.datetime, dt.datetime(2015, 3, 2, 11, 30, 0))
        self.assertAlmostEqual(txn.value, Decimal(120.))
