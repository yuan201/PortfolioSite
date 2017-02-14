import logging

from django.db import models
import pandas as pd

from core.types import PositiveDecimalField
from securities.models import Security

logger = logging.getLogger('quotes_model')


class Quote(models.Model):
    """
    In this app, only close quote is used right now
    """
    security = models.ForeignKey(Security, on_delete=models.CASCADE, related_name='quotes')
    date = models.DateField()
    open = PositiveDecimalField(default=0)
    close = PositiveDecimalField(default=0)
    high = PositiveDecimalField(default=0)
    low = PositiveDecimalField(default=0)
    volume = PositiveDecimalField(default=0)

    class Meta:
        get_latest_by = 'date'

    def __str__(self):
        return "{symbol}@{date}:[{open:.2f}, {close:.2f}, {high:.2f}, {low:.2f}, {volume:.2f}]".format(
            symbol=self.security.symbol,
            date=self.date,
            open=self.open,
            close=self.close,
            high=self.high,
            low=self.low,
            volume=self.volume,
        )

    @classmethod
    def update_quotes(cls, new_quotes_df, security, mode):
        old_quotes = cls.objects.filter(security=security)
        old_quotes_df = cls.to_DataFrame(old_quotes)
        old_dates = old_quotes_df.index
        new_dates = new_quotes_df.index
        # logger.debug('old_dates:{}'.format(old_dates))
        # logger.debug('new_dates:{}'.format(new_dates))
        if mode == 'append':
            append_dates = new_dates.difference(old_dates)
            # logger.debug('append_dates:{}'.format(append_dates))
            cls.add_quotes(new_quotes_df.ix[append_dates], security)
        elif mode == 'overwrite':
            intersection = new_dates.intersection(old_dates)
            if intersection.size > 0:
                overwrite_qs = cls.objects.filter(security=security).\
                                   filter(date__gte=intersection.min()).\
                                   filter(date__lte=intersection.max()).delete()
            cls.add_quotes(new_quotes_df, security)
        elif mode == 'discard':
            old_quotes.delete()
            cls.add_quotes(new_quotes_df, security)

    @classmethod
    def add_quotes(cls, quotes_df, security):
        for date, quote in quotes_df.iterrows():
            cls.objects.create(security=security,
                               date=date,
                               open=quote['open'],
                               close=quote['close'],
                               high=quote['high'],
                               low=quote['low'],
                               volume=quote['volume'])

    # todo queryset to dataframe sounds like a general util function
    @classmethod
    def to_DataFrame(cls, qs):
        """convert QuerySet to DataFrame"""
        dates = [pd.to_datetime(x[0]) for x in qs.values_list('date')]
        data = qs.values('open', 'close', 'high', 'low', 'volume')
        df = pd.DataFrame.from_records(data, index=dates)
        return df
