from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import Portfolio
from core.mixins import PortfoliosTestMixin
from todos.models import Todo


# todo: add unittests for context
# todo: add unittests for template


class HomePageTest(PortfoliosTestMixin, TestCase):

    def setUp(self):
        Portfolio.objects.create(name='Value')
        Portfolio.objects.create(name='Growth')

    def test_home_page_use_proper_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'homepage.html')

    def test_home_page_get_all_todos(self):
        response = self.client.get('/')
        self.assertEqual(response.context['todo'], Todo)


class NewPortfolioPageTest(PortfoliosTestMixin, TestCase):

    def test_add_new_portfolio(self):
        self.client.post(reverse('portfolios:new'),
                         data={'name': 'Value', 'description':'value portfolios'})
        self.assertEqual(Portfolio.objects.first().name, 'Value')
        self.assertEqual(Portfolio.objects.first().description, 'value portfolios')

    def test_new_portfolio_view_use_proper_template(self):
        response = self.client.get(reverse('portfolios:new'))
        self.assertTemplateUsed(response, 'portfolio/new_portfolio.html')

    def test_add_portfolio_view_redirect_to_detail_view(self):
        response = self.client.post(reverse('portfolios:new'),
                                    data={'name': 'Value', 'description': 'value portfolios'})
        p = Portfolio.objects.first()
        self.assertRedirects(response, reverse('portfolios:detail', args=[p.id]))

    def test_new_portfolio_has_prompt(self):
        response = self.client.get(reverse('portfolios:new'))
        self.assertContains(response, 'Basic Information')
        self.assertContains(response, 'Name')
        self.assertContains(response, 'Description')

    def test_can_not_add_portfolio_with_existing_name(self):
        Portfolio.objects.create(name='value', description='test')
        response = self.client.post(reverse('portfolios:new'),
                                    data={'name': 'value', 'description': 'simple value'})
        self.assertEqual(Portfolio.objects.count(), 1)

