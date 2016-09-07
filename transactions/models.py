from datetime import datetime, date
from decimal import getcontext

from django.db import models
from django.core.urlresolvers import reverse
from django.core import validators
from django.core.validators import ValidationError

from core.utils import build_link
from .exceptions import SellMoreThanHold

from core.types import PositiveDecimalField
from securities.models import Security


class Transaction(models.Model):
    """
    The Transactions model is a base model for all types of transactions
    """
    security = models.ForeignKey(Security)
    datetime = models.DateTimeField()
    portfolio = models.ForeignKey("portfolio.Portfolio", on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __lt__(self, other_txn):
        return self.datetime < other_txn.datetime

    def get_absolute_url(self):
        return reverse('portfolios:detail', args=[self.portfolio.id])


class BuyTransaction(Transaction):
    """
    A BuyTransaction represents a buy.
    """
    price = PositiveDecimalField()
    shares = models.PositiveIntegerField()
    fee = PositiveDecimalField()

    def __str__(self):
        return "On {} Buy {} share of {}({}) @ {}".format(
            self.datetime, self.shares, self.security.name, self.security.symbol, self.price
        )

    def cash_value(self):
        return -self.price * self.shares - self.fee

    def as_p(self):
        return str(self)

    def as_t(self):
        return "<td>{type}</td>" \
                "<td>{date:%Y-%m-%d}</td>" \
                "<td>{name}</td>" \
                "<td>{symbol}</td>" \
                "<td>{shares}</td>" \
                "<td>{price:.2f}</td>" \
                "<td>{fee:.2f}</td>" \
                "<td>{cash_value:.2f}</td>" \
                "<td>{ratio}</td>" \
                "<td>{del_link}</td>" \
                "<td>{update_link}</td>".format(
                type="Buy",date=self.datetime, name=self.security.name,
                symbol=self.security.symbol, shares=self.shares,
                price=self.price, fee=self.fee, cash_value=self.cash_value(),
                ratio='',
                del_link=build_link(reverse('transactions:del_buy', args=[self.id]), 'Del'),
                update_link=build_link(reverse('transactions:update_buy', args=[self.id]), 'Update'),
        )

    def transact(self, holding):
        """
        the transact function operate on a holding according to the transaction and
        return the new holding
        :param holding:
        :return holding:
        """
        holding.shares += self.shares
        holding.cost += self.cash_value()
        return holding


class SellTransaction(Transaction):
    """
    A SellTransaction represents a sell.
    """
    price = PositiveDecimalField()
    shares = models.PositiveIntegerField()
    fee = PositiveDecimalField()

    def __str__(self):
        return "On {} Sell {} share of {}({}) @ {}".format(
            self.datetime, self.shares, self.security.name, self.security.symbol, self.price
        )

    def cash_value(self):
        return self.price * self.shares - self.fee

    def as_p(self):
        return str(self)

    def as_t(self):
        return "<td>{type}</td>" \
                "<td>{date:%Y-%m-%d}</td>" \
                "<td>{name}</td>" \
                "<td>{symbol}</td>" \
                "<td>{shares}</td>" \
                "<td>{price:.2f}</td>" \
                "<td>{fee:.2f}</td>" \
                "<td>{cash_value:.2f}</td>" \
                "<td>{ratio}</td>" \
                "<td>{del_link}</td>" \
                "<td>{update_link}</td>".format(
                type="Sell",date=self.datetime, name=self.security.name,
                symbol=self.security.symbol, shares=self.shares,
                price=self.price, fee=self.fee, cash_value=self.cash_value(),
                ratio='',
                del_link=build_link(reverse('transactions:del_sell', args=[self.id]), 'Del'),
                update_link=build_link(reverse('transactions:update_sell', args=[self.id]), 'Update'),
                )

    def transact(self, holding):
        """
        the transact function operate on a holding, raise SellMoreThanHold if the holding
        doesn't have enough shares to sell. Otherwise, it removes the shares from the holding,
        calculate the gain/loss based on average cost and return new holding.
        :param holding:
        :return holding:
        """
        if self.shares > holding.shares:
            raise SellMoreThanHold
        cost_s = holding.cost_per_share()
        holding.shares -= self.shares
        holding.cost += cost_s * self.shares
        holding.gain += (self.price - cost_s) * self.shares - self.fee
        return holding


class DividendTransaction(Transaction):
    """
    A DividendTransaction represents dividend from the security.
    """
    value = PositiveDecimalField()

    def __str__(self):
        return "On {}, {}({}) paid {} dividend".format(
            self.datetime, self.security.name, self.security.symbol, self.value
        )

    def as_p(self):
        return str(self)

    def as_t(self):
        return "<td>{type}</td>" \
                "<td>{date:%Y-%m-%d}</td>" \
                "<td>{name}</td>" \
                "<td>{symbol}</td>" \
                "<td>{shares}</td>" \
                "<td>{price}</td>" \
                "<td>{fee}</td>" \
                "<td>{cash_value:.2f}</td>" \
                "<td>{ratio}</td>" \
                "<td>{del_link}</td>" \
                "<td>{update_link}</td>".format(
                type="Dividend", date=self.datetime, name=self.security.name,
                symbol=self.security.symbol, shares='', price='', fee='',
                cash_value=self.value, ratio='',
                del_link=build_link(reverse('transactions:del_dividend', args=[self.id]), 'Del'),
                update_link=build_link(reverse('transactions:update_dividend', args=[self.id]), 'Update'),
                )

    def transact(self, holding):
        holding.dividend += self.value
        return holding


class SplitTransaction(Transaction):
    """
    A SplitTransaction represents split/reverse split of a security.
    """
    ratio = PositiveDecimalField()

    def __str__(self):
        return "On {}, {}({}) split {}".format(
            self.datetime, self.security.name, self.security.symbol, self.ratio
        )

    def as_p(self):
        return str(self)

    def as_t(self):
        return "<td>{type}</td>" \
                "<td>{date:%Y-%m-%d}</td>" \
                "<td>{name}</td>" \
                "<td>{symbol}</td>" \
                "<td>{shares}</td>" \
                "<td>{price}</td>" \
                "<td>{fee}</td>" \
                "<td>{cash_value}</td>" \
                "<td>{ratio:.2f}</td>" \
                "<td>{del_link}</td>" \
                "<td>{update_link}</td>".format(
                type="Split", date=self.datetime, name=self.security.name,
                symbol=self.security.symbol, shares='', price='', fee='',
                cash_value='', ratio=self.ratio,
                del_link=build_link(reverse('transactions:del_split', args=[self.id]), 'Del'),
                update_link=build_link(reverse('transactions:update_split', args=[self.id]), 'Update'),
                )

    def transact(self, holding):
        holding.shares = int(holding.shares * self.ratio)
        return holding


class Holding():
    """
    A Holding is one item in a portfolio. It represents a particular security, how much
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


