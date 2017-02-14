from .quoter import Quoter
from quotes.models import Quote
from securities.models import Security


class QuoterLocal(Quoter):
    """
    Use the data stored in local database
    """
    def get_quotes(self, security, start, end):
        quotes = Quote.objects.filter(symbol=security.symbol).filter(date__gte=start).filter(date__lte=end)
        return Quote.to_DataFrame(quotes)

    def get_last_close(self, security):
        sec = Security.objects.get(symbol=security.symbol)
        return sec.quotes.latest().close

    def get_close(self, security, date):
        sec = Security.objects.get(symbol=security.symbol)
        return Quote.objects.get(security=sec.id, date=date).close
