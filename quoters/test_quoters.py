import unittest

from .quoter import QuoterTushare, SymbolNotExist


class TestQuotersTushare(unittest.TestCase):

    def test_quotertushare_can_return_quotes(self):
        qtr = QuoterTushare()
        gldq = qtr.get_quotes('000651', '2016-01-01', '2016-09-07')

        self.assertAlmostEqual(gldq.ix['2016-09-07']['open'], 22.9)
        self.assertAlmostEqual(gldq.ix['2016-01-04']['close'], 20.26)

    def test_quotertushare_raise_exception_for_wrong_symbol(self):
        qtr = QuoterTushare()

        with self.assertRaises(SymbolNotExist):
            qtr.get_quotes('abc', None, None)
