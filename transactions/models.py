from datetime import datetime, date

from django.db import models
from django.core.urlresolvers import reverse


class Security(models.Model):

    symbol = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
    currency = models.CharField(max_length=10, default='')

    def __str__(self):
        return "{}({})".format(self.name, self.symbol)

    def __repr__(self):
        return "Security(name={},symbol={},currency={}".format(
            self.name, self.symbol, self.currency
        )


class Transaction(models.Model):

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

    price = models.DecimalField(decimal_places=4, max_digits=15)
    shares = models.IntegerField()
    fee = models.DecimalField(decimal_places=4, max_digits=15)

    def __str__(self):
        return "On {} Buy {} share of {}({}) @ {}".format(
            self.datetime, self.shares, self.security.name, self.security.symbol, self.price
        )

    def cash_value(self):
        return -self.price * self.shares - self.fee

    def as_t(self):
        return "<td>{type}</td>" \
                "<td>{date:%Y-%m-%d}</td>" \
                "<td>{name}</td>" \
                "<td>{symbol}</td>" \
                "<td>{shares}</td>" \
                "<td>{price:.2f}</td>" \
                "<td>{fee:.2f}</td>" \
                "<td>{cash_value:.2f}</td>" \
                "<td>{ratio}</td>".format(
                type="Buy",date=self.datetime, name=self.security.name,
                symbol=self.security.symbol, shares=self.shares,
                price=self.price, fee=self.fee, cash_value=self.cash_value(),
                ratio='',
        )

    def transact(self, holding):
        holding.shares += self.shares
        holding.cost += self.cash_value()
        return holding


class SellTransaction(Transaction):

    price = models.DecimalField(decimal_places=4, max_digits=15)
    shares = models.IntegerField()
    fee = models.DecimalField(decimal_places=4, max_digits=15)

    def __str__(self):
        return "On {} Sell {} share of {}({}) @ {}".format(
            self.datetime, self.shares, self.security.name, self.security.symbol, self.price
        )

    def cash_value(self):
        return self.price * self.shares - self.fee

    def as_t(self):
        return "<td>{type}</td>" \
                "<td>{date:%Y-%m-%d}</td>" \
                "<td>{name}</td>" \
                "<td>{symbol}</td>" \
                "<td>{shares}</td>" \
                "<td>{price:.2f}</td>" \
                "<td>{fee:.2f}</td>" \
                "<td>{cash_value:.2f}</td>" \
                "<td>{ratio}</td>".format(
                type="Sell",date=self.datetime, name=self.security.name,
                symbol=self.security.symbol, shares=self.shares,
                price=self.price, fee=self.fee, cash_value=self.cash_value(),
                ratio='',
                )

    def transact(self, holding):
        if self.shares > holding.shares:
            raise SellMoreThanHold
        cost_s = holding.cost_per_share()
        holding.shares -= self.shares
        holding.cost += cost_s * self.shares
        holding.gain += (self.price - cost_s) * self.shares - self.fee
        return holding


class SellMoreThanHold(Exception):
    pass


class DividendTrasaction(Transaction):

    value = models.DecimalField(decimal_places=4, max_digits=15)

    def __str__(self):
        return "On {}, {}({}) paid {} dividend".format(
            self.datetime, self.security.name, self.security.symbol, self.value
        )

    def as_t(self):
        return "<td>{type}</td>" \
                "<td>{date:%Y-%m-%d}</td>" \
                "<td>{name}</td>" \
                "<td>{symbol}</td>" \
                "<td>{shares}</td>" \
                "<td>{price}</td>" \
                "<td>{fee}</td>" \
                "<td>{cash_value:.2f}</td>" \
                "<td>{ratio}</td>".format(
                type="Dividend", date=self.datetime, name=self.security.name,
                symbol=self.security.symbol, shares='', price='', fee='',
                cash_value=self.value, ratio='',
                )

    def transact(self, holding):
        holding.dividend += self.value
        return holding


class SplitTransaction(Transaction):

    ratio = models.DecimalField(decimal_places=4, max_digits=10)

    def __str__(self):
        return "On {}, {}({}) split {}".format(
            self.datetime, self.security.name, self.security.symbol, self.ratio
        )

    def as_t(self):
        return "<td>{type}</td>" \
                "<td>{date:%Y-%m-%d}</td>" \
                "<td>{name}</td>" \
                "<td>{symbol}</td>" \
                "<td>{shares}</td>" \
                "<td>{price}</td>" \
                "<td>{fee}</td>" \
                "<td>{cash_value}</td>" \
                "<td>{ratio:.2f}</td>".format(
                type="Split", date=self.datetime, name=self.security.name,
                symbol=self.security.symbol, shares='', price='', fee='',
                cash_value='', ratio=self.ratio,
                )

    def transact(self, holding):
        holding.shares = int(holding.shares * self.ratio)
        return holding


class Holding():

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
        return -self.cost/self.shares


