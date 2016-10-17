import logging
from collections import defaultdict
from decimal import Decimal

from django.db import models
from django.core.urlresolvers import reverse

from core.types import PositiveDecimalField
from securities.models import Security
from core.types import positive_validator

logger = logging.getLogger(__name__)

# todo refactor
# todo add parameters


class Benchmark(models.Model):
    """
    A benchmark is different from a portfolios in the way securities are added.
    In a portfolios, securities are added by shares (100 shares, etc).
    While for a benchmark, securities(normally an index) is added by a percentage
    such as 50% HS300 and 50% S&P500.
    When share prices change, a security's weight in a portfolios floats with the price
    while for a security in a benchmark, it's weight never changes.
    """
    name = models.CharField(max_length=50, default='', unique=True)
    description = models.TextField(default='')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('benchmarks:detail', args=[self.id])

    def _update_performance(self):
        last_quotes = {}
        performances = {}
        constitutes = {con.security.symbol: con for con in self.constitutes.all()}

        for con in self.constitutes.all():
            for quote in con.security.quotes.order_by('date'):
                sym = con.security.symbol
                if sym not in last_quotes:
                    last_quotes[sym] = quote.close
                else:
                    if quote.date not in performances:
                        performances[quote.date] = BenchmarkPerformance(
                            benchmark=self, date= quote.date,
                            change=quote.close/last_quotes[sym]*constitutes[sym].percent)
                    else:
                        performances[quote.date].change += \
                            quote.close/last_quotes[sym]*constitutes[sym].percent
                    last_quotes[sym] = quote.close

        for p in performances.values():
            p.save()

    def normalize_and_update(self):
        self.normalize()
        BenchmarkPerformance.objects.filter(benchmark=self).delete()
        self._update_performance()

    def normalize(self):
        total_percent = Decimal(0.)
        for cst in self.constitutes.all():
            total_percent += cst.percent

        for cst in self.constitutes.all():
            cst.percent = cst.percent/total_percent
            cst.save()

    def is_normalized(self):
        sum = 0
        for con in self.constitutes.all():
            sum += con.percent
        return (sum-1) < 1e-6


class BenchmarkConstitute(models.Model):
    security = models.ForeignKey(Security)
    percent = PositiveDecimalField()
    benchmark = models.ForeignKey(Benchmark,
                                  on_delete=models.CASCADE,
                                  related_name="constitutes")

    def __str__(self):
        return "{benchmark}->{security}:{percent:.2f}".format(
            benchmark=self.benchmark.name,
            security=self.security.name,
            percent=self.percent,
        )

    def get_absolute_url(self):
        return self.benchmark.get_absolute_url()


class BenchmarkPerformance(models.Model):
    benchmark = models.ForeignKey(Benchmark, related_name="performances")
    date = models.DateField()
    change = models.FloatField()

    def __str__(self):
        return "@{},{}:{:.1f}%".format(self.date, self.benchmark.name, (self.change-1)*100)
