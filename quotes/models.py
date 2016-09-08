from django.db import models

from core.types import PositiveDecimalField
from securities.models import Security


class Quote(models.Model):
    """
    In this app, only close quote is used.
    """
    security = models.ForeignKey(Security)
    date = models.DateField()
    open = PositiveDecimalField()
    close = PositiveDecimalField()
    high = PositiveDecimalField()
    low = PositiveDecimalField()
    volume = PositiveDecimalField()

    def __str__(self):
        return "{name}({symbol})@{date}:[{open:.2f}, {close:.2f}, {high:.2f}, {low:.2f}, {volume:.2f}]".format(
            name=self.security.name,
            symbol=self.security.symbol,
            date=self.date,
            open=self.open,
            close=self.close,
            high=self.high,
            low=self.low,
            volume=self.volume,
        )
