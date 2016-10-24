import factory

from .models import Security


class SecurityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Security

    symbol = factory.Sequence(lambda n: '600{:03d}'.format(n))
    currency = 'CNY'
    quoter = 'Tushare'
