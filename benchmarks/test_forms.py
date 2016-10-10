from django.test import TestCase

from .forms import ConstituteCreateForm
from .factories import BenchmarkFactory
# todo add unit tests for benchmark forms


class ConstituteCreateFormTest(TestCase):

    def setUp(self):
        self.bk = BenchmarkFactory.create()
        # self.form = ConstituteCreateForm()

    def test_normal_case(self):
        pass

