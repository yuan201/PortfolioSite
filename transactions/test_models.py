from django.test import TestCase

from securities.models import Security


class BuyTransactionTest(TestCase):

    def setUp(self):
        self.s1 = Security.objects.create(name='民生银行', symbol='MSYH', currency='RMB', isindex=False)

        