from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import BuyTransaction, SellTransaction, SplitTransaction
from .models import DividendTrasaction, Holding


class BuyTransactionModelTest(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_output_proper_table_line(self):
        pass


