import datetime as dt
import math

from django.db import models
from django.core.urlresolvers import reverse
import pandas as pd
import numpy as np

from core.utils import build_link
from core.config import CURRENCY_CHOICES


class Security(models.Model):
    """
    The Security model is used to represent a security that can be
    traded on some market.
    """
    symbol = models.CharField(max_length=20, unique=True)
    # name = models.CharField(max_length=50)
    currency = models.CharField(max_length=3, default='CNY', choices=CURRENCY_CHOICES)
    quoter = models.CharField(max_length=20, blank=True)
    isindex = models.BooleanField(default=False, verbose_name='Is this an Index?')

    def __str__(self):
        return "{}".format(self.symbol)

    def __repr__(self):
        return "Security(symbol={},currency={},quoter={},index={}".format(
            self.symbol, self.currency, self.quoter, self.isindex
        )

    def get_absolute_url(self):
        return reverse('securities:detail', args=[self.id])

    def as_t(self):
        last_quote = "<td></td>"
        if self.quotes.count() > 0:
            # todo define meta property in model class to use latest() instead
            last_quote = "<td>{q:.2f}</td>".format(q=self.quotes.order_by("-date").first().close)

        return "<td>{symbol}</td>" \
            "<td>{currency}</td>" \
            "<td>{quote_count}</td>".format(
                symbol=build_link(reverse('securities:detail', args=[self.id]), self.symbol),
                currency=self.currency, quote_count=self.quotes.count()) + last_quote

    def as_p(self):
        return str(self)

    def first_quote_before(self, _date):
        return self.quotes.filter(date__lte=_date).first()

    def quotes_between(self, start, end):
        rng = pd.bdate_range(start, end)
        quotes = pd.DataFrame(index=rng, columns=['open', 'close', 'high', 'low', 'volume'])

        for q in self.quotes.filter(date__gte=start).filter(date__lte=end).all():
            self.copy_query_to_dataframe(quotes.ix[q.date], q)

        if math.isnan(quotes['close'][0]):
            # no quote for the start date, try to acquire an older one instead
            early_quote = self.first_quote_before(start)
            if early_quote is None:
                return None
            self.copy_query_to_dataframe(quotes.ix[start], early_quote)

        return quotes.fillna(method='ffill')

    # todo define a utility function to copy this
    @staticmethod
    def copy_query_to_dataframe(df, query):
        df['open'] = query.open
        df['close'] = query.close
        df['high'] = query.high
        df['low'] = query.low
        df['volume'] = query.volume


class SecurityInfo(models.Model):
    """Information related to a security. Expected to change, but not very often. (e.g. shares outstanding"""

    security = models.ForeignKey(Security, on_delete=models.CASCADE, related_name='infos')
    valid_date = models.DateField(verbose_name='Valid Date')
    name = models.CharField(max_length=50, verbose_name='Name')
    industry = models.CharField(max_length=50, verbose_name='Industry', null=True)
    total_shares = models.FloatField(verbose_name='Total Shares', null=True)
    outstanding_shares = models.FloatField(verbose_name='Outstanding Shares', null=True)
    list_date = models.DateField(verbose_name='Date got Listed', null=True)

    class Meta:
        unique_together = ("security", "valid_date")
        get_latest_by = "valid_date"

    def __str__(self):
        return "{}@{}".format(self.name, self.valid_date)
