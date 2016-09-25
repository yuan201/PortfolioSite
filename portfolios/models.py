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
from core.utils import day_start


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
        if not date is None:
            hld.date = date
        hld.id = None
        hld.save(force_insert=True)

    def update_holdings(self, end):
        if Holding.objects.filter(portfolio=self):
            holding = Holding.objects.filter(portfolio=self).order_by('date').last()
            cur_date = pd.Timestamp(holding.date, offset='B') + 1
        else:
            holding = None
            cur_date = pd.Timestamp(day_start(self.transactions()[0].datetime), offset='B')

        for txn in self.transactions():
            logger.debug('working on ' + str(txn))
            if txn.datetime < cur_date:  # the transaction has already be processed
                continue

            if day_start(txn.datetime) > cur_date:  # we'd done all the transactions for cur_date, save it and move on
                self.insert_holding(holding)
                logger.debug('save ' + str(holding))
                cur_date += 1

                # fill the gaps
                while day_start(txn.datetime) > cur_date:
                    self.insert_holding(holding, cur_date)
                    logger.debug('save ' + str(holding))
                    cur_date += 1

            if day_start(txn.datetime) == cur_date:  # the transaction is for the current date, process it
                if not holding:
                    if not isinstance(txn, BuyTransaction):
                        raise FirstTransactionNotBuy
                    holding = Holding(security=txn.security, portfolio=self, date=cur_date)
                else:
                    holding.date = cur_date
                holding = txn.transact(holding)
        self.insert_holding(holding)



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
