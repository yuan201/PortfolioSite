import logging

from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import Security
from core.mixins import PortfoliosTestMixin

logger = logging.getLogger(__name__)


class NewSecViewTest(PortfoliosTestMixin, TestCase):

    def test_can_post_a_new_sec(self):
        self.client.post(reverse('securities:new'), data={
            'symbol': 'MSYH',
            'name': '民生银行',
            'currency': 'CNY',
        })

        sec = Security.objects.first()
        self.assertEqual(sec.symbol, 'MSYH')
        self.assertEqual(sec.name, '民生银行')
        self.assertEqual(sec.currency, 'CNY')

    def test_cannot_post_an_existing_sec(self):
        Security.objects.create(symbol='MSYH', name='民生银行', currency='CNY')

        response = self.client.post(reverse('securities:new'), data={
            'symbol': 'MSYH',
            'name': '民生银行',
            'currency': 'CNY',
        })

        self.assertEqual(Security.objects.count(), 1)
        self.assertFormError(response, 'form', 'symbol',
                             "Security with this Symbol already exists.")


class UpdateSecViewTest(PortfoliosTestMixin, TestCase):

    def test_can_update_a_sec(self):
        s1 = Security.objects.create(symbol='MSYH', name='民生银行', currency='CNY')

        self.client.post(reverse('securities:update', args=[s1.id]), data={
            'symbol': 'WKB',
            'name': '万科B',
            'currency': 'USD',
        })

        s2 = Security.objects.first()
        self.assertEqual(Security.objects.count(), 1)
        self.assertEqual(s1, s2)

    def test_cannot_update_sec_to_collide_with_existing_one(self):
        Security.objects.create(symbol='MSYH', name='民生银行', currency='CNY')
        s1 = Security.objects.create(symbol='MSH', name='民生银行', currency='HKD')

        response = self.client.post(reverse('securities:update', args=[s1.id]), data={
            'symbol': 'MSYH',
            'name': '民生银行',
            'currency': 'HKD',
        })

        self.assertFormError(response, 'form', 'symbol',
                             "Security with this Symbol already exists.")
        self.assertEqual(s1.symbol, 'MSH')

    def test_update_view_show_proper_info(self):
        s1 = Security.objects.create(symbol='MSYH', name='民生银行', currency='CNY')
        response = self.client.get(reverse('securities:update', args=[s1.id]))
        self.assertContains(response, s1.name)
        self.assertContains(response, s1.symbol)
        self.assertContains(response, s1.currency)


class DeleteSecViewTest(PortfoliosTestMixin, TestCase):

    def setUp(self):
        self.s1 = Security.objects.create(symbol='MSYH', name='民生银行', currency='CNY')

    def test_can_delete_a_sec(self):
        self.client.post(reverse('securities:del', args=[self.s1.id]))
        self.assertEqual(Security.objects.count(), 0)

    def test_sec_delete_view_show_prompt(self):
        response = self.client.get(reverse('securities:del', args=[self.s1.id]))
        self.assertContains(response, str(self.s1))


class DetailSecViewTest(PortfoliosTestMixin, TestCase):

    def setUp(self):
        self.s1 = Security.objects.create(symbol='MSYH', name='民生银行', currency='CNY')

    def test_detail_view_show_sec_info(self):
        response = self.client.get(reverse('securities:detail', args=[self.s1.id]))
        self.assertContains(response, self.s1.name)
        self.assertContains(response, self.s1.symbol)
        self.assertContains(response, self.s1.currency)

    def test_detail_view_has_delete_link(self):
        response = self.client.get(reverse('securities:detail', args=[self.s1.id]))
        # logger.debug(response.rendered_content)
        self.assertIn(reverse('securities:del', args=[self.s1.id]), response.rendered_content)

    def test_detail_view_has_update_link(self):
        response = self.client.get(reverse('securities:detail', args=[self.s1.id]))
        self.assertIn(reverse('securities:update', args=[self.s1.id]), response.rendered_content)

