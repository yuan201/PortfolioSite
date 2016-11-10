import factory
import datetime as dt

from .models import Security, SecurityInfo


class SecurityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Security

    symbol = factory.Sequence(lambda n: '600{:03d}'.format(n))
    currency = 'CNY'
    exchange = 'Shanghai'
    list_date = dt.date(1998, 10, 25)


class SecInfoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SecurityInfo

    valid_date = dt.date.today()
