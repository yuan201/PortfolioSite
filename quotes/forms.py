import logging

from django import forms
import pandas as pd
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import Submit
from django.core.urlresolvers import reverse_lazy

from quoters.quoter import SymbolNotExist, UnknownQuoter, Quoter
from quotes.models import Quote
from quotes.tasks import task_get_quote


logger = logging.getLogger('quotes_view')

# todo change MODE_CHOICES to use sensible phrase instead of 1,2,3
MODE_CHOICES = (('1', 'Append'), ('2', 'Overwrite'), ('3', 'Discard Existing'))
QUOTERS = (('Tushare', 'Tushare'), ('Xueqiu', 'Xueqiu'))

class QuotesForm(forms.Form):
    start = forms.DateField(
        widget=forms.TextInput(attrs={'placeholder': 'Start Date'}),
        required=True,)

    end = forms.DateField(
        widget=forms.TextInput(attrs={'placeholder': 'End Date'}),
        required=True,)

    quoter = forms.ChoiceField(choices=QUOTERS, required=True)

    mode = forms.ChoiceField(widget=forms.RadioSelect, choices=MODE_CHOICES, required=True)

    def __init__(self, *args, **kwargs):
        self.security = kwargs.pop('security')
        super(QuotesForm, self).__init__(*args, **kwargs)
        self.quotes = pd.DataFrame()
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('get', 'Get'))

    def clean(self):
        cleaned_data = super(QuotesForm, self).clean()
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')

        logger.debug('in clean')

        if start >= end:
            msg = u'end date before start date'
            self.add_error('start', msg)
            return cleaned_data

        if not self.security.exchange:
            msg = u'Exchange not specified'
            self.add_error(None, msg)
            return cleaned_data

        try:
            quoter = Quoter.quoter_factory(cleaned_data['quoter'])
        except UnknownQuoter:
            msg = u'Unknow Quoter'
            self.add_error('quoter', msg)

        try:
            self.quotes = task_get_quote(security=self.security, quoter=quoter,
                                       start=start.isoformat(), end=end.isoformat())
            logger.debug('getting quotes for {}, from {} to {}'.format(
                self.security.symbol, start.isoformat(), end.isoformat())
            )
            logger.debug('get {} quotes'.format(self.quotes['open'].count()))
        except SymbolNotExist:
            msg = u'symbol not found on this quoter'
            self.add_error(None, msg)

        return cleaned_data

    def save(self):
        self.save_quotes()

    def save_quotes(self):
        logger.debug('saving {} quotes to db, mode:{}'.format(
            self.quotes['open'].count(), self.cleaned_data['mode']))
        Quote.update_quotes(
            new_quotes_df=self.quotes,
            security=self.security,
            mode=self.cleaned_data['mode'],
        )


# todo remove separate view for updating quotes and use the inline form alone
class QuotesFormHorizontal(QuotesForm):
    mode = forms.ChoiceField(choices=MODE_CHOICES, required=True)

    def __init__(self, *args, **kwargs):
        super(QuotesFormHorizontal, self).__init__(*args, **kwargs)
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            'start',
            'end',
            'mode',
        )
        self.fields['start'].label = ''
        self.fields['end'].label = ''
        self.fields['mode'].label = ''
