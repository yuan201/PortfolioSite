import pandas as pd
import tushare as ts

from quotes.models import Quote


class SymbolNotExist(Exception):
    pass


class UnknownQuoter(Exception):
    pass


# todo need to wrap pandas web engine
class Quoter(object):
    """
    A Quoter give back quotes for a security or index.
    """
    def get_quotes(self, symbol, start, end):
        raise NotImplemented

    def get_last_close(self, symbol):
        raise NotImplemented

    def get_close(self, symbol, start, end):
        raise NotImplemented

    def get_adjusted_close(self):
        raise NotImplemented


class QuoterTushare(Quoter):
    """
    Use the TuShare library to get quote. This should work fine for all securities listed
    in China.
    """
    def get_quotes(self, symbol, start, end):
        quotes = ts.get_h_data(symbol, start=start, end=end, autype=None)
        if quotes is not None:
            # convert string based index to  DatatimeIndex
            dt_index = [pd.to_datetime(i) for i in quotes.index]
            quotes.index = dt_index
            return quotes[['open', 'close', 'high', 'low', 'volume']]
        else:
            raise SymbolNotExist()


class QuoterLocal(Quoter):
    """
    Use the data stored in local database
    """
    def get_quotes(self, symbol, start, end):
        quotes = Quote.objects.filter(symbol=symbol).filter(date__gte=start).filter(date__lte=end)


def quoter_factory(quoter):
    if quoter == "Tushare":
        return QuoterTushare()
    else:
        raise UnknownQuoter
