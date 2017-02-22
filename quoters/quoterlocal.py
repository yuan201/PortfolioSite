from .quoter import Quoter
from quotes.models import Quote
from securities.models import Security


class QuoterLocal(Quoter):
    """
    Use the data stored in local database
    """
    def get_quotes(self, security, start, end):
        quotes = Quote.objects.filter(symbol=security).filter(date__gte=start).filter(date__lte=end)
        return Quote.to_DataFrame(quotes)

    def get_last_close(self, security, date=None):
        if date is None:
            return security.quotes.latest().close
        else:
            return Quote.objects.filter(security=security).filter(date__lte=date).latest().close

    def get_close(self, security, date):
        return Quote.objects.get(security=security, date=date).close

