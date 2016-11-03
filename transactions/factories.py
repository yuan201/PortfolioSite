import factory
from .models import Transaction2


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction2


def transaction_factory(type, portfolio, security, datetime, **kwargs):
    return TransactionFactory(type=type,
                              portfolio=portfolio,
                              security=security,
                              datetime=datetime,
                              **kwargs)
