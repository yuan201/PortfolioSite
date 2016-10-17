import datetime as dt

import factory

from benchmarks.models import Benchmark, BenchmarkConstitute, BenchmarkPerformance
from securities.factories import SecurityFactory


class BenchConsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BenchmarkConstitute

    security = factory.SubFactory(SecurityFactory)
    percent = 1.
    benchmark = factory.SubFactory('benchmarks.factories.BenchmarkFactory')


class BenchPermFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BenchmarkPerformance

    date = factory.LazyFunction(dt.date.today)
    change = 1.1
    benchmark = factory.SubFactory('benchmarks.factories.BenchmarkFactory')


class BenchmarkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Benchmark

    name = factory.Sequence(lambda n: 'TestBK%s' % n)



