from django.db import models

from portfolios.models import Portfolio
from securities.models import Security
from benchmarks.models import Benchmark
from core.types import PositiveDecimalField, DecimalField


class Performance(models.Model):
    """Base model for store performance related data for securities, portfolios and benchmarks"""
    date = models.DateField()
    value = DecimalField(default=0)
    gain = DecimalField(default=0)
    cash_flow = DecimalField(default=0)

    class Meta:
        get_latest_by = 'date'
        abstract = True

    def calculate_gain(self):
        pass

    def twrr(self, start, end):
        pass

    def mwrr(self, start, end):
        pass


class BenchmarkPerformance(Performance):
    benchmark = models.ForeignKey(Benchmark, on_delete=models.CASCADE)


class PortfolioPerformance(Performance):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)


class SecurityPerformance(Performance):
    security = models.ForeignKey(Security, on_delete=models.CASCADE)
