import logging
from collections import defaultdict
from decimal import Decimal
from itertools import chain

from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
import pandas as pd
import numpy as np
from pandas.tseries.offsets import YearBegin

from securities.models import Security
from transactions.exceptions import FirstTransactionNotBuy
from benchmarks.models import Benchmark
from core.types import PositiveDecimalField, PerformanceSummary
from core.utils import date_, build_link
from core.utils import to_business_timestamp, last_business_day
from quotes.models import Quote
from quoters.quoter import Quoter
from core.exceptions import PortfolioException
from core.config import INIT_DATE, EXCHANGE_DEFAULT_QUOTER
from exchangerates.models import ExchangeRate
from core.config import BASE_CURRENCY, CURRENCY_CHOICES, DAYS_IN_A_YEAR
from .position import Position
from quoters.quotertushare import QuoterTushare
from quotes.forms import QuotesForm


class WrongTxnType(PortfolioException):
    pass


class NoPerformanceRecord(PortfolioException):
    pass


# todo figure out a proper structure for logging
logger = logging.getLogger(__name__)


class Portfolio(models.Model):
    """
    Class for managing portfolios
    """
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

    @staticmethod
    def insert_holding(hld, date=None):
        if date is not None:
            hld.date = date
        hld.id = None
        hld.save(force_insert=True)

    def _get_latest_record_or_empty(self, txn):
        try:
            return self.holdings.filter(security=txn.security).latest()
        except Holding.DoesNotExist:
            return Holding(security=txn.security, portfolio=self, date=date_(txn.datetime))

    #def fill_in_gaps(self, hld, gaps):
    #    for d in gaps:
    #        self.insert_holding(hld, d)

    @staticmethod
    def _transact_and_save(hld, txn):
        hld = txn.transact(hld)
        hld.save()
        txn.processed = True
        txn.save()

    def remove_all_holdings(self):
        self.holdings.all().delete()
        for txn in self.transactions.all():
            txn.processed = False
            txn.save()

    def remove_holdings_after(self, security, datetime):
        """removing holdings after a specific date"""
        self.holdings.filter(security=security).filter(date__gte=datetime).delete()

    def update_holdings(self, end=None):
        if not self.transactions.all():
            return

        if end is None:
            end = last_business_day()

        hlds = {}
        for txn in self.transactions.order_by('datetime').all():
            sym = txn.security.symbol

            if sym not in hlds:  # Transaction for a new security
                # find the latest holding record for this symbol
                # if found, the current transaction must has been processed in the past and will
                # be skipped below
                # if not found, start an empty holding record here
                hlds[sym] = self._get_latest_record_or_empty(txn)

            # convert date into pandas timestamp with business offset to automatically skip holidays
            hld_date = to_business_timestamp(hlds[sym].date)
            txn_date = to_business_timestamp(date_(txn.datetime))

            if txn_date < hld_date:  # already processed in the past
                continue
            elif txn_date == hld_date: # there might be multiple transactions for a day
                if not txn.processed:
                    self._transact_and_save(hlds[sym], txn)
            else: # txn_date > hld_date
                # self.fill_in_gaps(hlds[sym], pd.bdate_range(start=hld_date+1, end=txn_date-1))
                self.insert_holding(hlds[sym], txn_date)
                self._transact_and_save(hlds[sym], txn)

        # fill the gaps between last transaction and end
        # for sym, hld in hlds.items():
        #    self.fill_in_gaps(hld, pd.bdate_range(start=to_business_timestamp(hld.date)+1, end=end))

    def sum_each_currency(self, date=None):
        """Summary the value of the portfolio for each currency at a particular date"""
        return self.position(date).sum_each_currency()

    def total_value(self, date=None):
        """calculate the total value of the portfolio for a particular day"""
        return self.position(date).total_value()

    def position(self, date=None):
        # there are gaps in the holding database when there is no transaction.
        # so we need to find all the securities in the portfolio first and then
        # find their last holding info before the date
        if date is None:
            date = last_business_day()

        pos = Position(self.holdings.filter(security=hld.security).filter(date__lte=date).latest()
                       for hld in self.holdings.filter(date__lte=date).distinct('security'))

        for hld in pos:
            hld.date = date
            hld.update_value(save_to_db=False)
        return pos

    def update_performance(self):
        self.performance.update(self, append=True, end_date=last_business_day())

    def cash_flow(self, date):
        nextday = date + 1
        transactions = self.transactions.filter(datetime__gte=date).filter(datetime__lt=nextday).all()
        cf = 0
        for t in transactions:
            cf += t.cash_value
        return cf

    def twrr(self, start, end, annualize=False):
        qs = self.performance.filter(date__gt=start).filter(date__lte=end)
        if qs.count() == 0:
            raise NoPerformanceRecord

        gain = Decimal(1)

        for p in qs.all():
            gain *= p.gain/100+1

        if annualize:
            gain **= Decimal(DAYS_IN_A_YEAR/qs.count())

        return gain-1

    def mwrr(self, start, end, annualize=False):
        """
        calculate money weighted rate of return
        portfolio value right before start is considered initial cost
        and portfolio is assumed to sell at the end to calculate final value
        """
        drange = pd.bdate_range(start+1, end, offset='B')
        values = np.zeros(len(drange)+1)

        values[0] = -self.position(start).total_value()
        for i, d in enumerate(drange):
            values[i+1] = self.cash_flow(d)
        values[-1] += float(self.position(end).total_value())

        values = np.trim_zeros(values, 'f')
        # remove zeros from the front which represents days without any holding or transactions
        # this will not impact np.irr but changes the data length when calculate total mwrr
        irr = np.irr(values)
        if annualize:
            irr = np.power(irr+1, DAYS_IN_A_YEAR) - 1
        else:
            irr = np.power(irr+1, len(values)-1) - 1
        return Decimal(irr)

    def performance_summary(self):
        summary = {}
        end = last_business_day()

        if self.performance.count() == 0:
            return summary

        summary['twrr'] = PerformanceSummary(
            last_week=self.twrr(start=end-5, end=end),
            last_year=self.twrr(start=end-DAYS_IN_A_YEAR, end=end),
            ytd=self.twrr(start=to_business_timestamp(end-YearBegin(1)), end=end)
        )
        summary['mwrr'] = PerformanceSummary(
            last_week=self.mwrr(start=end-5, end=end),
            last_year=self.mwrr(start=end-DAYS_IN_A_YEAR, end=end),
            ytd=self.mwrr(start=to_business_timestamp(end-YearBegin(1)), end=end)
        )

        return summary

    def update_quotes(self):
        for hld in self.holdings.distinct('security'):
            self.update_sec_quotes(security=hld.security,
                                   quoter=EXCHANGE_DEFAULT_QUOTER[hld.security.exchange])

    def update_sec_quotes(self, security, quoter):
        if security.quotes.count() > 0:
            start = to_business_timestamp(security.quotes.latest().date) + 1
        else:
            start = INIT_DATE
        data = {'start': start,
                'end': last_business_day(),
                'mode': 'append',
                'quoter': quoter}
        form = QuotesForm(data=data, security=security)
        if form.is_valid():
            form.save()


class Holding(models.Model):
    """
    Security holdings for a portfolio, only record for those days there is at least one transaction
    """
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

    def update_value(self, save_to_db=True):
        quoter = Quoter.quoter_factory('Local')
        try:
            close = quoter.get_last_close(self.security, self.date)
        except Quote.DoesNotExist:
            pass
            # TODO add feature to enable auto quotes update when missing
        else:
            self.value = close * self.shares
            if save_to_db:
                self.save()

    @classmethod
    def update_all_values(cls, portfolio):
        for hld in cls.objects.filter(portfolio=portfolio).all():
            hld.update_value()





