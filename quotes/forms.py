import logging

from django import forms
import pandas as pd

from quoters.quoter import quoter_factory, SymbolNotExist, UnknownQuoter
from quotes.models import Quote

logger = logging.getLogger('quotes_view')


class QuotesForm(forms.Form):
    start = forms.DateField(required=True)
    end = forms.DateField(required=True)
    MODE_CHOICES = (('1', 'Append'), ('2', 'Overwrite'), ('3', 'Discard Existing'))
    mode = forms.ChoiceField(widget=forms.RadioSelect, choices=MODE_CHOICES, required=True)

    def __init__(self, *args, **kwargs):
        self.security = kwargs.pop('security')
        super(QuotesForm, self).__init__(*args, **kwargs)
        self.quotes = pd.DataFrame()

    def clean(self):
        cleaned_data = super(QuotesForm, self).clean()
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')

        if start >= end:
            msg = u'end date before start date'
            self.add_error('start', msg)
            return cleaned_data

        if self.security.quoter == '':
            msg = u'Quoter not specified'
            self.add_error(None, msg)
            return cleaned_data

        try:
            qtr = quoter_factory(self.security.quoter)
        except UnknownQuoter:
            msg = u'Unknown Quoter'
            self.add_error(None, msg)
            return cleaned_data

        try:
            self.quotes = qtr.get_quotes(self.security.symbol,
                                         start=start.isoformat(),
                                         end=end.isoformat())
            logger.debug('getting quotes for {}, from {} to {}'.format(
                self.security.symbol, start.isoformat(), end.isoformat())
            )
            logger.debug('get {} quotes'.format(self.quotes['open'].count()))
        except SymbolNotExist:
            msg = u'symbol not found on this quoter'
            self.add_error(None, msg)

        return cleaned_data

    def save_quotes(self):
        logger.debug('saving {} quotes to db, mode:{}'.format(
            self.quotes['open'].count(), self.cleaned_data['mode']))
        mode = self.cleaned_data['mode']
        Quote.update_quotes(new_quotes_df=self.quotes, security=self.security, mode=mode)


