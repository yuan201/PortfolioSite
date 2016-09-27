import datetime as dt

from django.test import TestCase
from .models import Benchmark, BenchmarkConstitute, BenchmarkPerformance
from securities.models import Security
from quotes.models import Quote


class BenchmarkModelTest(TestCase):

    def setUp(self):
        self.bk1 = Benchmark.objects.create(name='BK1', description='simple benchmark')
        self.s1 = Security.objects.create(name='格力电器', symbol='GLDQ')
        self.s2 = Security.objects.create(name='民生银行', symbol='MSYH')
        self.bc1 = BenchmarkConstitute.objects.create(security=self.s1, benchmark=self.bk1, percent=0.3)
        self.bc2 = BenchmarkConstitute.objects.create(security=self.s2, benchmark=self.bk1, percent=0.7)

    def test_model_str(self):
        self.assertEqual(str(self.bk1), 'BK1')

    def test_model_update_performance(self):
        Quote.objects.create(security=self.s1, date=dt.date(2016, 1, 1), close=100)
        Quote.objects.create(security=self.s1, date=dt.date(2016, 1, 4), close=110)
        Quote.objects.create(security=self.s1, date=dt.date(2016, 1, 5), close=132)
        Quote.objects.create(security=self.s2, date=dt.date(2016, 1, 5), close=12.96)
        Quote.objects.create(security=self.s2, date=dt.date(2016, 1, 4), close=14.4)
        Quote.objects.create(security=self.s2, date=dt.date(2016, 1, 1), close=12)

        self.bk1.update_performance()

        bps = {bp.date: bp for bp in BenchmarkPerformance.objects.all()}
        self.assertEqual(len(bps), 2)
        self.assertAlmostEqual(bps[dt.date(2016, 1, 4)].change, 1.17)
        self.assertAlmostEqual(bps[dt.date(2016, 1, 5)].change, 0.99)


class BenchmarkConstitutesModelTest(TestCase):

    def setUp(self):
        self.bk1 = Benchmark.objects.create(name='BK1', description='simple benchmark')
        self.s1 = Security.objects.create(name='民生银行', symbol='MSYH')

    def test_str(self):
        bc1 = BenchmarkConstitute.objects.create(security=self.s1, benchmark=self.bk1, percent=1.0)
        self.assertEqual(str(bc1), "BK1->民生银行:1.00")


class BenchmarkPerformanceModelTest(TestCase):

    def setUp(self):
        self.bk1 = Benchmark.objects.create(name='BK1', description='test bk')
        self.bp1 = BenchmarkPerformance.objects.create(
            benchmark=self.bk1, date=dt.date(2016, 9, 1), change=1.23
        )

    def test_str(self):
        self.assertEqual(str(self.bp1), "@2016-09-01,BK1:23.0%")
