import datetime as dt

from django.db import models
from django.core.urlresolvers import reverse

from transactions.models import BuyTransaction, SellTransaction, \
    SplitTransaction, DividendTransaction, Security, HoldingCls
from benchmarks.models import Benchmark
from core.types import PositiveDecimalField


class WrongTxnType(Exception):
    pass


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


class Holding(models.Model):
    security = models.ForeignKey(Security)
    portfolio = models.ForeignKey(Portfolio)
    shares = models.IntegerField(default=0)
    cost = PositiveDecimalField()
    gain = PositiveDecimalField()
    dividend = PositiveDecimalField()
    value = PositiveDecimalField()

    def transact(self, txn):
        return txn.transact(self)

    def __str__(self):
        return "{name}({symbol}):{shares}shares,cost{cost}\n" \
                "value={value},dividend={dividend},gain={gain}".format(
                name=self.security.name, symbol=self.security.symbol,
                shares=self.shares, cost=self.cost,
                dividend=self.dividend, gain=self.gain, value=self.value
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
