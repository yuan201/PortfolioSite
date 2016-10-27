from django.forms import ModelForm, ValidationError

from .models import Security, SecurityInfo


class NewSecurityForm(ModelForm):
    class Meta:
        model = Security
        fields = ['symbol', 'currency', 'quoter', 'isindex']


class NewSecurityInfoForm(ModelForm):
    # todo update valid info and throw away invalid ones instead of reject everything

    def __init__(self, *args, **kwargs):
        self.last = kwargs.pop('last', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.last is None:
            return cleaned_data

        if (cleaned_data.get('name') == self.last.name and
            cleaned_data.get('industry') == self.last.name and
            cleaned_data.get('total_shares') == self.last.total_shares and
            cleaned_data.get('outstanding_shares') == self.last.outstanding_shares and
            cleaned_data.get('list_date') == self.last.list_date):
            msg = u"Nothing changed"
            self.add_error(msg)

        return cleaned_data

    class Meta:
        model = SecurityInfo
        fields = ['security', 'valid_date', 'name', 'industry', 'total_shares', 'outstanding_shares',
                  'list_date']
