import factory
from .models import Transaction


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction


def transaction_factory(type, portfolio, security, datetime, **kwargs):
    return TransactionFactory(type=type,
                              portfolio=portfolio,
                              security=security,
                              datetime=datetime,
                              **kwargs)
