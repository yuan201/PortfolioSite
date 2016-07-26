from unittest import skip
from datetime import datetime, tzinfo, timezone

from django.test import TestCase
from django.core.urlresolvers import reverse

from. models import BuyTransaction, SellTransaction, DividendTrasaction
from .models import SplitTransaction, Holding, Security
from portfolio.models import Portfolio


class NewTransactionTestBase(TestCase):

    def setUp(self):
        self.s1 = Security.objects.create(name='Google', symbol='GOOG', currency='USD')
        self.s2 = Security.objects.create(name='Apple', symbol='APPL', currency='USD')
        self.p1 = Portfolio.objects.create(name='BigCap', description='Test')


class BuyTransactionCreateViewTest(NewTransactionTestBase):

    def test_can_post_a_new_buy_txn(self):
        response = self.client.post(reverse('transactions:add_buy', args=[self.p1.id]), data={
            'security': '1',
            'datetime': '2015-1-1 15:00:00',
            'price': '15.0',
            'shares': '100',
            'fee': '10',
        })

        txn = BuyTransaction.objects.first()
        self.assertEqual(txn.security, self.s1)
        self.assertEqual(txn.portfolio, self.p1)
        self.assertEqual(txn.datetime, datetime(2015, 1, 1, 15, 0, 0, tzinfo=timezone.utc))
        self.assertEqual(txn.price, 15.0)
        self.assertEqual(txn.shares, 100)
        self.assertEqual(txn.fee, 10.0)

