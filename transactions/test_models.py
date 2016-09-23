import datetime as dt

from django.test import TestCase
from django.core.urlresolvers import reverse

from securities.models import Security
from portfolios.models import Portfolio, Holding
from .models import BuyTransaction, SellTransaction, DividendTransaction, SplitTransaction
from transactions.exceptions import SellMoreThanHold, DividendOnEmptyHolding


class BuyTransactionTest(TestCase):

    def setUp(self):
        self.s1 = Security.objects.create(name='民生银行', symbol='MSYH', currency='RMB', isindex=False)
        self.p1 = Portfolio.objects.create(name='Value', description='Test Value')
        self.txn = BuyTransaction.objects.create(
            security=self.s1,
            datetime=dt.datetime(2016, 1, 1, 10, 30),
            portfolio=self.p1,
            price=10.1,
            shares=100,
            fee=5.2,
        )

    def test_str(self):
        self.assertEqual(str(self.txn),
                         "On 2016-01-01 10:30:00 Buy 100 shares of 民生银行(MSYH) @ 10.1")

    def test_cash_value(self):
        self.assertAlmostEqual(self.txn.cash_value(), -1015.2)

    def test_as_p(self):
        self.assertEqual(self.txn.as_p(), str(self.txn))

    def test_as_t(self):
        self.assertHTMLEqual(self.txn.as_t(), '<td>Buy</td><td>2016-01-01</td> \
        <td>民生银行</td><td>MSYH</td><td>100</td><td>10.10</td><td>5.20</td> \
        <td>-1015.20</td><td></td><td><a href="{del_link}">Del</a></td> \
        <td><a href="{update_link}">Update</a></td>'.format(
            del_link=reverse("transactions:del_buy", args=[self.txn.id]),
            update_link=reverse("transactions:update_buy", args=[self.txn.id])
            )
        )

    def test_transact_with_empty_holding(self):
        hld = Holding(security=self.s1, portfolio=self.p1, date=dt.date(2016, 1, 1))

        hld = self.txn.transact(hld)

        self.assertEqual(hld.shares, 100)
        self.assertEqual(hld.cost, -1015.2)
        self.assertEqual(hld.gain, 0)
        self.assertEqual(hld.dividend, 0)
        self.assertEqual(hld.value, 0)

    def test_transact_with_existing_holding(self):
        hld = Holding(security=self.s1, portfolio=self.p1, date=dt.date(2016, 1, 1),
                      shares=200, cost=-1500., gain=450.,)

        hld = self.txn.transact(hld)

        self.assertEqual(hld.shares, 300)
        self.assertAlmostEqual(hld.cost, -2515.2)
        self.assertAlmostEqual(hld.gain, 450.)


class SellTransactionTest(TestCase):

    def setUp(self):
        self.s1 = Security.objects.create(name='民生银行', symbol='MSYH', currency='RMB', isindex=False)
        self.p1 = Portfolio.objects.create(name='Value', description='Test Value')
        self.txn = SellTransaction.objects.create(
            security=self.s1,
            datetime=dt.datetime(2016, 1, 1, 9, 15),
            portfolio=self.p1,
            price=10.2,
            shares=200,
            fee=9.3,
        )

    def test_str(self):
        self.assertEqual(str(self.txn),
                         "On 2016-01-01 09:15:00 Sell 200 shares of 民生银行(MSYH) @ 10.2")

    def test_as_p(self):
        self.assertEqual(self.txn.as_p(), str(self.txn))

    def test_cash_value(self):
        self.assertAlmostEqual(self.txn.cash_value(), 2030.7)

    def test_as_t(self):
        self.assertHTMLEqual(self.txn.as_t(), '<td>Sell</td><td>2016-01-01</td> \
        <td>民生银行</td><td>MSYH</td><td>200</td><td>10.20</td><td>9.30</td> \
        <td>2030.70</td><td></td><td><a href="{del_link}">Del</a></td> \
        <td><a href="{update_link}">Update</a></td>'.format(
             del_link=reverse("transactions:del_sell", args=[self.txn.id]),
             update_link=reverse("transactions:update_sell", args=[self.txn.id]),
             )
        )

    def test_raise_on_empty_holding(self):
        hld = Holding(security=self.s1, portfolio=self.p1, date=dt.date(2016, 1, 1))

        with self.assertRaises(SellMoreThanHold):
            self.txn.transact(hld)

    def test_transact_on_proper_holding(self):
        hld = Holding(security=self.s1, portfolio=self.p1, date=dt.date(2016, 1, 1),
                      shares=300, cost=-1500., gain=450., )

        hld = self.txn.transact(hld)

        self.assertEqual(hld.shares, 100)
        self.assertAlmostEqual(hld.cost, -500)
        self.assertAlmostEqual(hld.gain, 1480.7)

    def test_transact_sell_all(self):
        hld = Holding(security=self.s1, portfolio=self.p1, date=dt.date(2016, 1, 1),
                      shares=200, cost=-1000., gain=100., )

        hld = self.txn.transact(hld)

        self.assertEqual(hld.shares, 0)
        self.assertEqual(hld.cost, 0)
        self.assertAlmostEqual(hld.gain, 1130.7)


class DividendTransactionTest(TestCase):
    def setUp(self):
        self.s1 = Security.objects.create(name='民生银行', symbol='MSYH', currency='RMB', isindex=False)
        self.p1 = Portfolio.objects.create(name='Value', description='Test Value')
        self.txn = DividendTransaction.objects.create(
            security=self.s1,
            datetime=dt.datetime(2016, 1, 1, 14, 20),
            portfolio=self.p1,
            value=120.,
        )

    def test_str(self):
        self.assertEqual(str(self.txn),
                         "On 2016-01-01 14:20:00 民生银行(MSYH) paid 120.0 dividend")

    def test_as_p(self):
        self.assertEqual(self.txn.as_p(), str(self.txn))

    def test_as_t(self):
        self.assertHTMLEqual(self.txn.as_t(), '<td>Dividend</td><td>2016-01-01</td> \
         <td>民生银行</td><td>MSYH</td><td></td><td></td><td></td> \
         <td>120.00</td><td></td><td><a href="{del_link}">Del</a></td> \
         <td><a href="{update_link}">Update</a></td>'.format(
              del_link=reverse('transactions:del_dividend', args=[self.txn.id]),
              update_link=reverse('transactions:update_dividend', args=[self.txn.id])
              )
         )

    def test_transact_raise_on_empty_holding(self):
        hld = Holding(security=self.s1, portfolio=self.p1, date=dt.date(2016, 1, 1))

        with self.assertRaises(DividendOnEmptyHolding):
            hld = self.txn.transact(hld)

    def test_transact_on_existing_holding(self):
        hld = Holding(security=self.s1, portfolio=self.p1, date=dt.date(2016, 1, 1),
                      shares=200, cost=-1000., gain=100., dividend=49.,)

        hld = self.txn.transact(hld)

        self.assertAlmostEqual(hld.dividend, 169.)
        self.assertEqual(hld.shares, 200)
        self.assertEqual(hld.cost, -1000)
        self.assertEqual(hld.gain, 100)


class SplitTransactionTest(TestCase):
    def setUp(self):
        self.s1 = Security.objects.create(name='民生银行', symbol='MSYH', currency='RMB', isindex=False)
        self.p1 = Portfolio.objects.create(name='Value', description='Test Value')
        self.txn = SplitTransaction.objects.create(
            security=self.s1,
            datetime=dt.datetime(2016, 1, 1, 11, 20),
            portfolio=self.p1,
            ratio=1.2
        )

    def test_str(self):
        self.assertEqual(str(self.txn),
                         "On 2016-01-01 11:20:00 民生银行(MSYH) split 1.2")

    def test_as_p(self):
        self.assertEqual(self.txn.as_p(), str(self.txn))

    def test_as_t(self):
        self.assertHTMLEqual(self.txn.as_t(), '<td>Split</td><td>2016-01-01</td> \
        <td>民生银行</td><td>MSYH</td><td></td><td></td><td></td><td></td> \
        <td>1.20</td><td><a href="{del_link}">Del</a></td> \
        <td><a href="{update_link}">Update</a></td>'.format(
             del_link=reverse('transactions:del_split', args=[self.txn.id]),
             update_link=reverse('transactions:update_split', args=[self.txn.id])
             )
        )

    def test_transact_on_existing_holding(self):
        hld = Holding(security=self.s1, portfolio=self.p1, date=dt.date(2016, 1, 1),
                      shares=200, cost=-1000., gain=100., dividend=49.,)

        hld = self.txn.transact(hld)

        self.assertEqual(hld.shares, 240)
        self.assertEqual(hld.cost, -1000.)
        self.assertEqual(hld.gain, 100.)
