import factory
from .models import ExchangeRate


class ExchangeRateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExchangeRate
