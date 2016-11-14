import logging
from collections import defaultdict
from decimal import Decimal
from itertools import chain

from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
import pandas as pd

from securities.models import Security
from transactions.exceptions import FirstTransactionNotBuy
from benchmarks.models import Benchmark
from core.types import PositiveDecimalField
from core.utils import date_, build_link
from core.utils import to_business_timestamp
from quotes.models import Quote
from quoters.quoter import Quoter


class WrongTxnType(Exception):
    pass

# todo figure out a proper structure for logging
logger = logging.getLogger(__name__)


class Portfolio(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(default='')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    benchmark = models.ForeignKey(Benchmark, null=True)

    class Meta:
        unique_together = (('name', 'owner'),)

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Portfolio({})'.format(self.__dict__)

    def get_absolute_url(self):
        return reverse('portfolios:detail', args=[self.id])

    # todo implement total value for portfolio
    def total_value(self, _date):
        """calculate the total value of the portfolio for a particular day"""
        pass

    @staticmethod
    def insert_holding(hld, date=None):
        if date is not None:
            hld.date = date
        hld.id = None
        hld.save(force_insert=True)

    def get_latest_record_or_empty(self, txn):
        try:
            return self.holdings.filter(security=txn.security).latest()
        except Holding.DoesNotExist:
            return Holding(security=txn.security, portfolio=self, date=date_(txn.datetime))

    def fill_in_gaps(self, hld, gaps):
        for d in gaps:
            self.insert_holding(hld, d)

    @staticmethod
    def _transact_and_save(hld, txn):
        hld = txn.transact(hld)
        hld.save()

    def update_holdings(self, end):
        if not self.transactions.all():
            return

        hlds = {}
        for txn in self.transactions.all():
            sym = txn.security.symbol

            if sym not in hlds:  # Transaction for a new security
                # find the latest holding record for this symbol
                # if found, the current transaction must has been processed in the past and will
                # be skipped below
                # if not found, start an empty holding record here
                hlds[sym] = self.get_latest_record_or_empty(txn)

            # convert date into pandas timestamp with business offset to automatically skip holidays
            # note holding record is kept for every business day, so detail time of the transaction
            # is stripped off.
            hld_date = to_business_timestamp(hlds[sym].date)
            txn_date = to_business_timestamp(date_(txn.datetime))

            if txn_date < hld_date:  # already processed in the past
                continue
            elif txn_date == hld_date: # there might be multiple transactions for a day
                self._transact_and_save(hlds[sym], txn)
            else: # txn_date > hld_date
                self.fill_in_gaps(hlds[sym], pd.bdate_range(start=hld_date+1, end=txn_date-1))
                self.insert_holding(hlds[sym], txn_date)
                self._transact_and_save(hlds[sym], txn)

        # fill the gaps between last transaction and end
        for sym, hld in hlds.items():
            self.fill_in_gaps(hld, pd.bdate_range(start=to_business_timestamp(hld.date)+1, end=end))

    def sum_each_currency(self, date=None):
        if not self.holdings:
            return {}

        if date is None:
            date = self.holdings.latest().date

        values = defaultdict(Decimal)
        holdings = Holding.objects.filter(portfolio=self).filter(date=date).all()

        for hld in holdings:
            values[hld.security.currency] += hld.value
        return values

    # todo try nested array instead
    def sum_currency_as_l(self):
        result = ""
        for currency, value in self.sum_each_currency().items():
            result += '<li>{}: {:.2f}</li>'.format(currency, value)
        return result

    # todo understand whether custom managers should be used
    def remove_holdings_after(self, security, datetime):
        """removing holdings after a specific date"""
        self.holdings.filter(security=security).filter(date__gte=datetime).delete()


class Holding(models.Model):
    security = models.ForeignKey(Security)
    portfolio = models.ForeignKey(Portfolio, related_name='holdings')
    shares = models.IntegerField(default=0)
    cost = PositiveDecimalField(default=0)
    gain = PositiveDecimalField(default=0)
    dividend = PositiveDecimalField(default=0)
    value = PositiveDecimalField(default=0)
    date = models.DateField()

    class Meta:
        get_latest_by = 'date'
        unique_together = ('security', 'portfolio', 'date')

    def transact(self, txn):
        return txn.transact(self)

    def __str__(self):
        return "@{date}:{portfolio} has {name}({symbol}):shares={shares},cost={cost:.2f}," \
                "value={value:.2f},dividend={dividend:.2f},gain={gain:.2f}".format(
                    name=self.security.name, symbol=self.security.symbol,
                    shares=self.shares, cost=self.cost,
                    dividend=self.dividend, gain=self.gain, value=self.value,
                    date=self.date, portfolio=self.portfolio.name,
                )

    # todo add utilities for common links (security, portfolio, currency, etc)
    def as_t(self):
        return "<td>{sec_link}</td>" \
                "<td>{symbol}</td>" \
                "<td>{currency}</td>" \
                "<td>{shares}</td>" \
                "<td>{cost:.2f}</td>" \
                "<td>{cost_s:.2f}</td>" \
                "<td>{value:.2f}</td>" \
                "<td>{dividend:.2f}</td>" \
                "<td>{gain:.2f}</td>".format(
                    sec_link=build_link(reverse('securities:detail', args=[self.security.id]), self.security.name),
                    symbol=self.security.symbol,
                    currency=self.security.currency, shares=self.shares,
                    cost=self.cost, cost_s=self.cost_per_share(),
                    dividend=self.dividend, gain=self.gain, value=self.value,
                )

    def cost_per_share(self):
        """
        The cost is generally a negative number representing cash outflow. Since cost per
        share is more interesting in absolute terms, the conversion is performed in the func.
        :return cost per share in absolute number:
        """
        if self.shares > 0:
            return -self.cost/self.shares
        return 0

    # todo use get() instead, probably within a try block
    # todo decouple all direct access to quote database and use Quoter interface instead
    def update_value(self):
        quoter = Quoter.quoter_factory('Local')
        try:
            close = quoter.get_close(self.security, self.date)
        except Quote.DoesNotExist:
            pass
        else:
            self.value = close * self.shares
            self.save()

    @classmethod
    def update_all_values(cls, portfolio):
        for hld in cls.objects.filter(portfolio=portfolio).all():
            hld.update_value()
