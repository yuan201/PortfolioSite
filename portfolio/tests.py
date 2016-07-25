from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import Portfolio


class HomePageTest(TestCase):

    def test_home_page_list_all_portfolios(self):
        Portfolio.objects.create(name='Value')
        Portfolio.objects.create(name='Growth')

        response = self.client.get('/')

        self.assertContains(response, 'Value')
        self.assertContains(response, 'Growth')

    def test_home_page_use_proper_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'homepage.html')


class NewPortfolioPageTest(TestCase):

    def test_add_new_portfolio(self):
        self.client.post(reverse('portfolios:new'), data={'name': 'Value', 'description':'value portfolio'})
        self.assertEqual(Portfolio.objects.first().name, 'Value')
        self.assertEqual(Portfolio.objects.first().description, 'value portfolio')


