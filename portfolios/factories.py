import factory
from .models import Portfolio, Holding
from users.factories import UserFactory


class PortfolioFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Portfolio

    name = factory.Sequence(lambda n: 'value{}'.format(n))
    owner = factory.SubFactory(UserFactory)


class HoldingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Holding

