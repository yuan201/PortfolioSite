import unittest
import pandas as pd

from securities.factories import SecurityFactory
from .quoter import SymbolNotExist, Quoter


# todo use mock in unit test
class TestQuotersTushare(unittest.TestCase):

    def test_quotertushare_can_return_quotes(self):
        sec = SecurityFactory(symbol='000651')
        qtr = Quoter.quoter_factory("Tushare")
        gldq = qtr.get_quotes(sec, '2016-01-01', '2016-09-07')

        self.assertAlmostEqual(gldq['open']['2016-09-07'][0], 22.9)
        self.assertAlmostEqual(gldq['close']['2016-01-04'][0], 20.26)

    def test_quotertushare_raise_exception_for_wrong_symbol(self):
        qtr = Quoter.quoter_factory("Tushare")
        sec = SecurityFactory(symbol='abc')

        with self.assertRaises(SymbolNotExist):
            qtr.get_quotes(sec, None, None)
