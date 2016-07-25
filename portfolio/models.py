from datetime import datetime, date

from django.db import models
from django.core.urlresolvers import reverse

from transactions.models import BuyTransaction, SellTransaction, \
    SplitTransaction, DividendTrasaction, Security, Holding


class Portfolio(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(default='')

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Portfolio({})'.format(self.name)

    def get_absolute_url(self):
        return reverse('portfolios:detail', args=[self.id])

    def transactions(self):
        txns = list(BuyTransaction.objects.filter(portfolio=self).all())
        txns += list(SellTransaction.objects.filter(portfolio=self).all())
        txns += list(DividendTrasaction.objects.filter(portfolio=self).all())
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
        return Holding(security=txn.security,
                        shares=txn.shares,
                        cost=txn.cash_value(),
                       )


class WrongTxnType(Exception):
    pass
