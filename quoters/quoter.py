class SymbolNotExist(Exception):
    pass


class UnknownQuoter(Exception):
    pass


# todo need to wrap pandas web engine
# todo find a source for all HK listed stocks
class Quoter(object):
    """
    A Quoter give back quotes for a security or index.
    """
    # todo replace symbol with security
    def get_quotes(self, symbol, start, end):
        """return quotes in DataFrame"""
        raise NotImplemented

    def get_last_close(self, symbol):
        raise NotImplemented

    def get_closes(self, symbol, start, end):
        """return closes in Series"""
        raise NotImplemented

    def get_adjusted_closes(self):
        raise NotImplemented

    def get_close(self, symbol, date):
        raise NotImplemented

    @classmethod
    def quoter_factory(cls, quoter):
        from .quoterlocal import QuoterLocal
        from .quotertushare import QuoterTushare
        from .quoterxueqiu import QuoterXueqiu
        from .quoterpandas import QuoterPandas
        if quoter == "Tushare":
            return QuoterTushare()
        elif quoter == "Local":
            return QuoterLocal()
        elif quoter == "Xueqiu":
            return QuoterXueqiu()
        elif quoter == "pandas":
            return QuoterPandas()
        else:
            raise UnknownQuoter

