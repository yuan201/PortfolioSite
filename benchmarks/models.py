import logging

from django.db import models
from django.core.urlresolvers import reverse

from core.types import PositiveDecimalField
from securities.models import Security
from core.types import positive_validator

logger = logging.getLogger(__name__)


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


class BenchmarkConstitute(models.Model):
    security = models.ForeignKey(Security)
    percent = models.FloatField(validators=[positive_validator])
    benchmark = models.ForeignKey(Benchmark,
                                  on_delete=models.CASCADE,
                                  related_name="constitutes")

    def __str__(self):
        return "{benchmark}->{security}:{percent:.2f}".format(
            benchmark=self.benchmark.name,
            security=self.security.name,
            percent=self.percent,
        )
