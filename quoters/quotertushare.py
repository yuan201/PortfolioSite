import pandas as pd
import tushare as ts
from time import sleep

from .quoter import Quoter, SymbolNotExist


class QuoterTushare(Quoter):
    """
    Use the TuShare library to get quote. This should work fine for all securities listed
    in China.
    """
    # todo implement other methods
    def get_quotes(self, symbol, start, end):
        for count in range(3):
            try:
                quotes = ts.get_h_data(symbol, start=start, end=end, autype=None, pause=1)
            except IOError as e:
                sleep(10)
            else:
                break

        if quotes is not None:
            # convert string based index to  DatatimeIndex
            dt_index = [pd.to_datetime(i) for i in quotes.index]
            quotes.index = dt_index
            return quotes[['open', 'close', 'high', 'low', 'volume']]
        else:
            raise SymbolNotExist()

    def get_last_close(self, symbol):
        pass
