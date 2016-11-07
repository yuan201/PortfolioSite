from datetime import datetime, date
from decimal import getcontext

from django.db import models
from django.core.urlresolvers import reverse
from django.core import validators
from django.core.validators import ValidationError

from core.utils import build_link
from .exceptions import SellMoreThanHold, DividendOnEmptyHolding, UnknownTransactionType

from core.types import PositiveDecimalField
from securities.models import Security


class HoldingCls():
    """
    A Holding is one item in a portfolios. It represents a particular security, how much
    shares has, total cost and any gain/loss, dividend received from this security.
    """
    def __init__(self, security, shares, cost):
        self.security = security
        self.shares = shares
        self.cost = cost
        self.gain = 0
        self.dividend = 0

    def transact(self, txn):
        return txn.transact(self)

    def __str__(self):
        return "{name}({symbol}):{shares}shares,cost{cost}\n" \
               "dividend={dividend},gain={gain}".format(
               name=self.security.name, symbol=self.security.symbol,
               shares=self.shares, cost=self.cost,
               dividend=self.dividend, gain=self.gain,
               )

    def as_t(self):
        return "<td>{name}</td>" \
               "<td>{symbol}</td>" \
               "<td>{currency}</td>" \
               "<td>{shares}</td>" \
               "<td>{cost:.2f}</td>" \
               "<td>{cost_s:.2f}</td>" \
               "<td>{dividend:.2f}</td>" \
               "<td>{gain:.2f}</td>".format(
               name=self.security.name, symbol=self.security.symbol,
               currency=self.security.currency, shares=self.shares,
               cost=self.cost, cost_s=self.cost_per_share(),
               dividend=self.dividend, gain=self.gain
               )

    def cost_per_share(self):
        """
        The cost is generally a negative number representing cash outflow. Since cost per
        share is more interesting in absolute terms, the conversion is performed in the func.
        :return cost per share in absolute number:
        """
        return -self.cost/self.shares


TXN_TYPE = [('buy', 'Buy'),
            ('sell', 'Sell'),
            ('dividend', 'Dividend'),
            ('split', 'Split')]


class Transaction(models.Model):
    security = models.ForeignKey(Security)
    datetime = models.DateTimeField()
    portfolio = models.ForeignKey("portfolios.Portfolio", on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=10, choices=TXN_TYPE)
    price = PositiveDecimalField(default=0, blank=True)
    shares = models.PositiveIntegerField(default=0, blank=True)
    fee = PositiveDecimalField(default=0, blank=True)
    dividend = PositiveDecimalField(default=0, blank=True)
    ratio = PositiveDecimalField(default=0, blank=True)

    class Meta:
        ordering = ['datetime']
        get_latest_by = ('datetime')

    STR_TMP = {'buy': 'On {datetime} Buy {shares} shares of {name}({symbol}) at {price:.2f}/share, fee:{fee:.2f}',
               'sell': 'On {datetime} Sell {shares} shares of {name}({symbol}) at {price:.2f}/share, fee:{fee:.2f}',
               'dividend': 'On {datetime} {name}({symbol}) pays dividend {dividend:.2f}',
               'split': 'On {datetime} {name}({symbol}) split 1:{ratio:.2f}'}

    @property
    def cash_value(self):
        if self.type=='buy':
            return -self.price * self.shares - self.fee
        elif self.type=='sell':
            return self.price * self.shares - self.fee
        elif self.type=='dividend' or self.type=='split':
            return 0
        else:
            raise UnknownTransactionType

    def _format_dict(self):
        d = self.__dict__
        d['name'] = self.security.name
        d['symbol'] = self.security.symbol
        d['cash_value'] = self.cash_value
        d['del_link'] = build_link(reverse('transactions:del', args=[self.id]), 'Del')
        d['update_link'] = build_link(reverse('transactions:update', args=[self.id]), 'Update')
        d['type_cap'] = self.type.capitalize()
        return d

    def __str__(self):
        return Transaction.STR_TMP[self.type].format(**self._format_dict())

    def as_p(self):
        return str(self)

    def as_t(self):
        result = "<tr class='{type}'> \
               <td>{type_cap}</td> \
               <td>{datetime:%Y-%m-%d}</td> \
               <td>{name}</td> \
               <td>{symbol}</td> \
               <td>{shares}</td> \
               <td>{price:.2f}</td> \
               <td>{fee:.2f}</td> \
               <td>{cash_value:.2f}</td> \
               <td>{dividend:.2f}</td> \
               <td>{ratio:.2f}</td> \
               <td>{del_link}</td> \
               <td>{update_link}</td></tr>".format(**self._format_dict())
        return result.replace('<td>0.00</td>', '<td></td>').replace('<td>0</td>', '<td></td>')

    def transact(self, holding):
        if self.type=='buy':
            holding.shares += self.shares
            holding.cost += self.cash_value
        elif self.type=='sell':
            if self.shares > holding.shares:
                raise SellMoreThanHold
            cost_s = holding.cost_per_share()
            holding.shares -= self.shares
            holding.cost += cost_s * self.shares
            holding.gain += (self.price - cost_s) * self.shares - self.fee
        elif self.type=='dividend':
            if holding.shares==0:
                raise DividendOnEmptyHolding
            holding.dividend += self.dividend
        elif self.type=='split':
            holding.shares = int(holding.shares * self.ratio)
        return holding

    def get_absolute_url(self):
        return reverse('portfolios:detail', args=[self.portfolio.id])

    def fill_in_defaults(self):
        if self.type == 'buy' or self.type == 'sell':
            self.dividend = 0.
            self.ratio = 0.
        else:
            self.price = 0.
            self.shares = 0
            self.fee = 0
        if self.type == 'dividend':
            self.ratio = 0
        if self.type == 'split':
            self.dividend = 0
