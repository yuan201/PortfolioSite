import datetime as dt

import factory

from .models import Quote
from securities.factories import SecurityFactory


class QuoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Quote

    security = factory.SubFactory(SecurityFactory)
    close = factory.sequence(lambda n: n+10)
    date = factory.lazy_attribute(dt.date.today)

