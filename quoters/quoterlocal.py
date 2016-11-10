from .quoter import Quoter
from quotes.models import Quote
from securities.models import Security


class QuoterLocal(Quoter):
    """
    Use the data stored in local database
    """
    # todo implement all methods
    def get_quotes(self, symbol, start, end):
        quotes = Quote.objects.filter(symbol=symbol).filter(date__gte=start).filter(date__lte=end)
        return Quote.to_DataFrame(quotes)

    def get_last_close(self, symbol):
        sec = Security.objects.get(symbol=symbol)
        return sec.quotes.latest().close

    def get_close(self, symbol, date):
        sec = Security.objects.get(symbol=symbol)
        return Quote.objects.get(security=sec.id, date=date).close
