from decimal import Decimal
from collections import defaultdict
import pandas as pd
import numpy as np

from core.utils import last_business_day
from core.config import BASE_CURRENCY

from exchangerates.models import ExchangeRate


class Position(list):
    """Holdings is a list of holding record that represents the holdings of a portfolio on a particular day"""
    def value(self, currency):
        value = Decimal(0)
        for hld in self:
            if hld.security.currency == currency:
                value += hld.value
        return value

    def total_value(self):
        if len(self) == 0:
            return Decimal(0)

        values = self.sum_each_currency()
        date = self[0].date
        total = Decimal()
        for currency, value in values.items():
            if currency == BASE_CURRENCY:
                total += value
            else:
                rate = ExchangeRate.objects.filter(currency=currency).filter(date__lte=date).latest().rate
                total += value * rate
        return total

    def sum_each_currency(self):
        values = defaultdict(Decimal)
        for hld in self:
            values[hld.security.currency] += hld.value
        return values

    def sum_currency(self):
        """
        function to build the string array for html output. The 'unordered_list' tag is required to turn
        the string array to html list.
        """
        result = []
        for currency, value in self.sum_each_currency().items():
            result.append("{}: {:.2f}".format(currency, value))
        return result
