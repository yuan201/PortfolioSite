import pandas as pd

from django.db import models

from portfolios.models import Portfolio
from securities.models import Security
from benchmarks.models import Benchmark
from core.types import PositiveDecimalField, DecimalField
from core.mixins import DateUtilMixin
from core.utils import last_business_day, to_business_timestamp
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
    def update(self, portfolio, end_date, append=False):
        performances = self.filter(portfolio=portfolio)
        if append and performances.count()>0:
            base_record = performances.latest()
            start_date = to_business_timestamp(base_record.date)+1
        else:
            base_record = PortfolioPerformance(portfolio=portfolio, value=0)
            start_date = portfolio.transactions.earliest().datetime

        for d in pd.date_range(start=start_date, end=end_date, freq='B'):
            pos = portfolio.position(d)
            cf = portfolio.cash_flow(d)
            if base_record.value > 0:
                gain = ((pos.total_value()-cf)/base_record.value-1)*100
            else:
                gain = 0

            new_record = PortfolioPerformance(
                portfolio=portfolio,
                date=d,
                value=pos.total_value(),
                cash_flow=cf,
                gain=gain,
            )
            new_record.save()
            base_record = new_record

    def remove_after(self, date):
        self.filter(date__gte=date).delete()


class PortfolioPerformance(Performance):
    portfolio = models.ForeignKey(Portfolio,
                                  on_delete=models.CASCADE,
                                  related_name='performance')
    objects = PortPerfManager()

    class Meta:
        unique_together = ('portfolio', 'date')
        get_latest_by = 'date'

    def __str__(self):
        return "{}@{}(value={}, cash flow={}, gain={:.3f}".format(self.portfolio.name, self.date, self.value,
                                                             self.cash_flow, self.gain)


class SecurityPerformance(Performance):
    security = models.ForeignKey(Security,
                                 on_delete=models.CASCADE,
                                 related_name='performance')
    pass
