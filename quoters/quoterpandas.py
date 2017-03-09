import pandas_datareader.data as web

from .quoter import Quoter, RemoteDataError, SymbolNotExist


class QuoterPandas(Quoter):

    def get_quotes(self, security, start, end):
        if security.exchange == 'HKEX':
            name = security.symbol[1:] + '.HK'
        else:
            raise SymbolNotExist

        try:
            data = web.DataReader(name=name, data_source='yahoo', start=start, end=end)
        except Exception:
            raise RemoteDataError
        data = data.rename(columns={"Open": "open", "Close": "close", "High": "high", "Low": "low", "Volume": "volume"})
        return data



