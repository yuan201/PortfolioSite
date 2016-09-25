import datetime as dt
import logging

from django.db import models
from django.core.urlresolvers import reverse
import pandas as pd

from transactions.models import BuyTransaction, SellTransaction, \
    SplitTransaction, DividendTransaction, Security, HoldingCls
from transactions.exceptions import FirstTransactionNotBuy
from benchmarks.models import Benchmark
from core.types import PositiveDecimalField
from core.utils import _date


class WrongTxnType(Exception):
    pass

logger = logging.getLogger(__name__)


class Portfolio(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(default='')
    benchmark = models.ForeignKey(Benchmark, null=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Portfolio({})'.format(self.name)

    def get_absolute_url(self):
        return reverse('portfolios:detail', args=[self.id])

    def transactions(self):
        txns = list(BuyTransaction.objects.filter(portfolio=self).all())
        txns += list(SellTransaction.objects.filter(portfolio=self).all())
        txns += list(DividendTransaction.objects.filter(portfolio=self).all())
        txns += list(SplitTransaction.objects.filter(portfolio=self).all())
        txns.sort()
        return txns

    def holdings(self, end_date_time):
        hlds = {}
        for txn in self.transactions():
            if txn.datetime.replace(tzinfo=None) > end_date_time:
                break
            if not txn.security in hlds:
                hlds[txn.security] = self.init_holding(txn)
            else:
                hlds[txn.security] = hlds[txn.security].transact(txn)
        return hlds

    def init_holding(self, txn):
        if not isinstance(txn, BuyTransaction):
            raise WrongTxnType
        return HoldingCls(security=txn.security,
                          shares=txn.shares,
                          cost=txn.cash_value(),
                          )

    def value(self, _date):
        """calculate the value of the portfolio for a particular day"""
        pass

    @staticmethod
    def insert_holding(hld, date=None):
        if date is not None:
            hld.date = date
        hld.id = None
        hld.save(force_insert=True)

    def find_last_record(self, security):
        if Holding.objects.filter(portfolio=self).filter(security=security):
            return Holding.objects.filter(portfolio=self).filter(security=security).order_by('date').last()
        return False

    def get_last_record_or_empty(self, txn):
        last_record = self.find_last_record(txn.security)
        if last_record:
            return last_record
        else:
            return Holding(security=txn.security, portfolio=self, date=txn.datetime)

    @staticmethod
    def fill_in_gaps(hld, _range):
        for d in _range:
            hld.date = d
            hld.id = None
            hld.save(force_insert=True)

    def update_holdings(self, end):
        if not self.transactions():
            return

        hlds = dict()
        dirty = False

        for txn in self.transactions():
            sym = txn.security.symbol
            dirty = False

            if sym not in hlds:  # Transaction for a new security
                hlds[sym] = self.get_last_record_or_empty(txn)

            hld_date = pd.Timestamp(hlds[sym].date, offset='B')
            txn_date = pd.Timestamp(_date(txn.datetime), offset='B')

            if txn_date < hld_date:  # already processed in the past
                continue

            if txn_date > hld_date:  # done with the current date, move on
                self.insert_holding(hlds[sym])
                if txn_date > hld_date+1: # there are days without a transaction
                    self.fill_in_gaps(hlds[sym], pd.bdate_range(start=hld_date+1, end=txn_date-1))
                hlds[sym].date = txn_date

            # since the gap has been filled, the current transaction is now for current date
            # just process it
            hlds[sym] = txn.transact(hlds[sym])
            dirty = True

        # fill the gaps between last transaction and end
        for sym, hld in hlds.items():
            if dirty:
                self.insert_holding(hld)
            hld_date = pd.Timestamp(hld.date, offset='B')
            if hld_date < end:
                self.fill_in_gaps(hld, pd.bdate_range(start=hld_date+1, end=end))

    def rebuild_holdings(self):
        """
        This methold discard all the existing holdings record for this portfolio and
        rebuild every from scratch
        :return:
        """
        Holding.objects.filter(portfolio=self).delete()


class Holding(models.Model):
    security = models.ForeignKey(Security)
    portfolio = models.ForeignKey(Portfolio)
    shares = models.IntegerField(default=0)
    cost = PositiveDecimalField(default=0)
    gain = PositiveDecimalField(default=0)
    dividend = PositiveDecimalField(default=0)
    value = PositiveDecimalField(default=0)
    date = models.DateField()

    def transact(self, txn):
        return txn.transact(self)

    def __str__(self):
        return "@{date}:{name}({symbol}):{shares}=shares,cost={cost:.2f}," \
                "value={value:.2f},dividend={dividend:.2f},gain={gain:.2f}".format(
                    name=self.security.name, symbol=self.security.symbol,
                    shares=self.shares, cost=self.cost,
                    dividend=self.dividend, gain=self.gain, value=self.value,
                    date=self.date,
                )

    def as_t(self):
        return "<td>{name}</td>" \
               "<td>{symbol}</td>" \
               "<td>{currency}</td>" \
               "<td>{shares}</td>" \
               "<td>{cost:.2f}</td>" \
               "<td>{cost_s:.2f}</td>" \
               "<td>{value:.2f}</td>" \
               "<td>{dividend:.2f}</td>" \
               "<td>{gain:.2f}</td>".format(
                   name=self.security.name, symbol=self.security.symbol,
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
        return -self.cost/self.shares
