import pandas as pd

from django.db import models

from portfolios.models import Portfolio
from securities.models import Security
from benchmarks.models import Benchmark
from core.types import PositiveDecimalField, DecimalField
from core.mixins import DateUtilMixin
from core.utils import last_business_day
from core.exceptions import PortfolioException


class AppendEmptyDatabaseException(PortfolioException):
    pass


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


class BenchmarkPerformance(Performance):
    benchmark = models.ForeignKey(Benchmark,
                                  on_delete=models.CASCADE,
                                  related_name='performance')
    pass


class PortPerfManager(models.Manager):
    def append(self, portfolio, end_date=None):
        if end_date is None:
            end_date = last_business_day()

        try:
            base_record = self.filter(portfolio=portfolio).earliest()
        except Performance.DoesNotExist:
            raise AppendEmptyDatabaseException

        for d in pd.date_range(start=self.append_date(), end=end_date, freq='B'):
            hld = portfolio.position(d)
            cf = portfolio.cash_flow(d)
            new_record = PortfolioPerformance(
                             date=d,
                             value=hld.total_value(),
                             gain=(hld.total_value() - cf)/base_record.total_value(),
                             cash_flow=cf
                             )
            new_record.save()
            base_record = new_record


class PortfolioPerformance(Performance):
    portfolio = models.ForeignKey(Portfolio,
                                  on_delete=models.CASCADE,
                                  related_name='performance')
    objects = PortPerfManager()



class SecurityPerformance(Performance):
    security = models.ForeignKey(Security,
                                 on_delete=models.CASCADE,
                                 related_name='performance')
    pass
