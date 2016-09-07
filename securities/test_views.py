from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import Security


class NewSecViewTest(TestCase):

    def test_can_post_a_new_sec(self):
        self.client.post(reverse('securities:new'), data={
            'symbol': 'MSYH',
            'name': '民生银行',
            'currency': 'RMB',
        })

        sec = Security.objects.first()
        self.assertEqual(sec.symbol, 'MSYH')
        self.assertEqual(sec.name, '民生银行')
        self.assertEqual(sec.currency, 'RMB')

    def test_cannot_post_an_existing_sec(self):
        Security.objects.create(symbol='MSYH', name='民生银行', currency='RMB')

        response = self.client.post(reverse('securities:new'), data={
            'symbol': 'MSYH',
            'name': '民生银行',
            'currency': 'RMB',
        })

        self.assertEqual(Security.objects.count(), 1)
        self.assertFormError(response, 'form', 'symbol',
                             "Security with this Symbol already exists.")


class UpdateSecViewTest(TestCase):

    def test_can_update_a_sec(self):
        s1 = Security.objects.create(symbol='MSYH', name='民生银行', currency='RMB')

        self.client.post(reverse('securities:update', args=[s1.id]), data={
            'symbol': 'WKB',
            'name': '万科B',
            'currency': 'USD',
        })

        s2 = Security.objects.first()
        self.assertEqual(Security.objects.count(), 1)
        self.assertEqual(s1, s2)

    def test_cannot_update_sec_to_collide_with_existing_one(self):
        Security.objects.create(symbol='MSYH', name='民生银行', currency='RMB')
        s1 = Security.objects.create(symbol='MSH', name='民生银行', currency='HKD')

        response = self.client.post(reverse('securities:update', args=[s1.id]), data={
            'symbol': 'MSYH',
            'name': '民生银行',
            'currency': 'HKD',
        })

        self.assertFormError(response, 'form', 'symbol',
                             "Security with this Symbol already exists.")
        self.assertEqual(s1.symbol, 'MSH')


class DeleteSecViewTest(TestCase):

    def test_can_delete_a_sec(self):
        s1 = Security.objects.create(symbol='MSYH', name='民生银行', currency='RMB')

        self.client.post(reverse('securities:del', args=[s1.id]))

        self.assertEqual(Security.objects.count(), 0)

