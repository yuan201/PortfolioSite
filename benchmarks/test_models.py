import datetime as dt
from decimal import Decimal

from django.test import TestCase
from django.core.urlresolvers import reverse
from .models import Benchmark, BenchmarkConstitute, BenchmarkPerformance
from securities.models import Security
from quotes.models import Quote
from .factories import BenchConsFactory, BenchmarkFactory, BenchPermFactory
from securities.factories import SecurityFactory


class BenchmarkModelTest(TestCase):

    def test_model_str(self):
        bk = BenchmarkFactory(name='BK1')
        self.assertEqual(str(bk), 'BK1')

    def test_get_absolute_url(self):
        bk = BenchmarkFactory()
        self.assertEqual(bk.get_absolute_url(), reverse('benchmarks:detail', args=[bk.id]))

    def setup_performance_records(self, percents):
        bk = BenchmarkFactory()
        s1, s2 = SecurityFactory.create_batch(2)
        BenchConsFactory(benchmark=bk, percent=percents[0], security=s1)
        BenchConsFactory(benchmark=bk, percent=percents[1], security=s2)
        Quote.objects.create(security=s1, date=dt.date(2016, 1, 1), close=100)
        Quote.objects.create(security=s1, date=dt.date(2016, 1, 4), close=110)
        Quote.objects.create(security=s1, date=dt.date(2016, 1, 5), close=132)
        Quote.objects.create(security=s2, date=dt.date(2016, 1, 5), close=12.96)
        Quote.objects.create(security=s2, date=dt.date(2016, 1, 4), close=14.4)
        Quote.objects.create(security=s2, date=dt.date(2016, 1, 1), close=12)
        return bk

    def test_model_update_performance(self):
        bk = self.setup_performance_records([3, 7])
        bk.normalize_and_update()

        bps = {bp.date: bp for bp in BenchmarkPerformance.objects.all()}
        self.assertEqual(len(bps), 2)
        self.assertAlmostEqual(bps[dt.date(2016, 1, 4)].change, 1.17)
        self.assertAlmostEqual(bps[dt.date(2016, 1, 5)].change, 0.99)

    def test_model_update_performance_after_normalize(self):
        bk = self.setup_performance_records([1, 1])
        bk.normalize_and_update()

        bps = {bp.date: bp for bp in BenchmarkPerformance.objects.all()}
        self.assertEqual(len(bps), 2)
        self.assertAlmostEqual(bps[dt.date(2016, 1, 4)].change, 1.15)
        self.assertAlmostEqual(bps[dt.date(2016, 1, 5)].change, 1.05)

    def test_is_not_normalized(self):
        bk = self.setup_performance_records([1, 1])
        self.assertFalse(bk.is_normalized())

    def test_is_normalized(self):
        bk = self.setup_performance_records([0.5, 0.5])
        self.assertTrue(bk.is_normalized())


class BenchmarkConstitutesModelTest(TestCase):

    def test_str(self):
        bc = BenchConsFactory(benchmark__name='BK1', percent=1., security__name='民生银行')
        self.assertEqual(str(bc), "BK1->民生银行:1.00")

    def test_normalize(self):
        bk = BenchmarkFactory()
        bc1 = BenchConsFactory.create_batch(5, percent=1., benchmark=bk)
        bk.normalize()

        bcs = BenchmarkConstitute.objects.all()
        for bc in bcs:
            self.assertAlmostEqual(bc.percent, Decimal(0.2))

    def test_get_absolute_url(self):
        bc = BenchConsFactory()
        self.assertEqual(bc.get_absolute_url(), reverse('benchmarks:detail', args=[bc.benchmark.id]))


class BenchmarkPerformanceModelTest(TestCase):

    def test_str(self):
        bp = BenchPermFactory(benchmark__name='BK1', change=1.23, date=dt.date(2016, 9, 1))
        self.assertEqual(str(bp), "@2016-09-01,BK1:23.0%")

