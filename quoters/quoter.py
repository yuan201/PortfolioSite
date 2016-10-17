import pandas as pd
import tushare as ts


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


class QuoterTushare(Quoter):
    """
    Use the TuShare library to get quote. This should work fine for all securities listed
    in China.
    """
    def get_quotes(self, symbol, start, end):
        quotes = ts.get_hist_data(symbol, start, end)
        if quotes is not None:
            # convert string based index to  DatatimeIndex
            dt_index = [pd.to_datetime(i) for i in quotes.index]
            quotes.index = dt_index
            return quotes[['open', 'close', 'high', 'low', 'volume']]
        else:
            raise SymbolNotExist()


def quoter_factory(quoter):
    if quoter == "Tushare":
        return QuoterTushare()
    else:
        raise UnknownQuoter
