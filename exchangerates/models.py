import datetime as dt

from django.db import models
from openexchangerates.exchange import Exchange
import pandas as pd

from core.utils import last_business_day, date_
from core.config import INIT_DATE, CURRENCY_CHOICES, BASE_CURRENCY
from core.types import PositiveDecimalField


class ExchangeRate(models.Model):
    date = models.DateField()
    currency = models.CharField(max_length=3, unique_for_date=date)
    rate = PositiveDecimalField()

    def __str__(self):
        return "@{}, '{}':{:.4f}".format(self.date, self.currency, self.rate)

    @classmethod
    def update_db(cls):
        last_db_date = INIT_DATE
        exchange = Exchange()

        if ExchangeRate.objects.all():
            last_db_date = ExchangeRate.objects.order_by('date').last().date
            last_db_date = pd.Timestamp(last_db_date, offset='B')+1

        for d in pd.bdate_range(start=last_db_date, end=last_business_day()):
            rates = exchange.historical_rates(d)
            for c in CURRENCY_CHOICES:
                if c[0] == BASE_CURRENCY:
                    continue
                cls.objects.create(date=date_(d), currency=c[0],
                                   rate=exchange.exchange(1, c[0], BASE_CURRENCY, rates))


