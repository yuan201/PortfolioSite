from django.test import TestCase
from .models import Benchmark, BenchmarkConstitute
from securities.models import Security


class BenchmarkModelTest(TestCase):

    def test_model_str(self):
        bk1 = Benchmark.objects.create(name='BK1', description='simple benchmark')
        self.assertEqual(str(bk1), 'BK1')


class BenchmarkConstitutesModelTest(TestCase):

    def setUp(self):
        self.bk1 = Benchmark.objects.create(name='BK1', description='simple benchmark')
        self.s1 = Security.objects.create(name='民生银行', symbol='MSYH', currency='RMB')

    def test_model_str(self):
        bc1 = BenchmarkConstitute.objects.create(security=self.s1, benchmark=self.bk1, percent=1.0)
        self.assertIn(self.s1.name, str(bc1))
        self.assertIn(self.bk1.name, str(bc1))
        self.assertIn(str("1.00"), str(bc1))