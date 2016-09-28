from django.test import TestCase

from .forms import ConstituteCreateForm

# todo add unit tests for benchmark forms


class ConstituteCreateFormTest(TestCase):

    def setUp(self):
        self.form = ConstituteCreateForm()
