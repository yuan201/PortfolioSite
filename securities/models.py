import datetime as dt
import math

from django.db import models
from django.core.urlresolvers import reverse
import pandas as pd
import numpy as np

from core.utils import build_link


class Security(models.Model):
    """
    The Security model is used to represent a security that can be
    traded on some market.
    """
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    currency = models.CharField(max_length=10, default='')
    quoter = models.CharField(max_length=20, blank=True)
    isindex = models.BooleanField(default=False)

    def __str__(self):
        return "{}({})".format(self.name, self.symbol)

    def __repr__(self):
        return "Security(name={},symbol={},currency={},quoter={},index={}".format(
            self.name, self.symbol, self.currency, self.quoter, self.isindex
        )

    def get_absolute_url(self):
        return reverse('securities:detail', args=[self.id])

    def as_t(self):
        last_quote = "<td></td>"
        if self.quotes.count() > 0:
            last_quote = "<td>{q:.2f}</td>".format(q=self.quotes.order_by("-date").first().close)

        return "<td>{symbol}</td>" \
                "<td>{name}</td>" \
                "<td>{currency}</td>" \
                "<td>{quote_count}</td>".format(
                symbol=build_link(reverse('securities:detail', args=[self.id]), self.symbol),
                name=self.name, currency=self.currency, quote_count=self.quotes.count()) + last_quote

    def as_p(self):
        return str(self)

    def quote_on(self, _date):
        """return the quote on the specified date or earlier"""
        return self.quotes.filter(date__lte=_date).first()

    def quote_between(self, start, end):
        rng = pd.bdate_range(start, end)
        quotes = pd.DataFrame(index=rng, columns=['open', 'close', 'high', 'low', 'volume'])

        for q in self.quotes.filter(date__gte=start).filter(date__lte=end).all():
            self.copy_query_to_dataframe(quotes.ix[q.date], q)

        if math.isnan(quotes['close'][0]):
            # no quote for the start date, try to acquire an older one instead
            early_quote = self.quote_on(start)
            if early_quote is None:
                return None
            self.copy_query_to_dataframe(quotes.ix[start], early_quote)

        return quotes.fillna(method='ffill')

    @staticmethod
    def copy_query_to_dataframe(df, query):
        df['open'] = query.open
        df['close'] = query.close
        df['high'] = query.high
        df['low'] = query.low
        df['volume'] = query.volume
