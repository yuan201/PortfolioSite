from django import forms

from quoters.quoter import quoter_factory, SymbolNotExist, UnknownQuoter


class QuotesForm(forms.Form):
    start = forms.DateField()
    end = forms.DateField()

    def __init__(self, **kwargs):
        self.security = kwargs.pop('security')
        super(QuotesForm, self).__init__(**kwargs)

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
        except SymbolNotExist:
            msg = u'symbol not found on this quoter'
            self.add_error(None, msg)

        return cleaned_data