from django.forms import ModelForm, ValidationError

from .models import Security, SecurityInfo


class NewSecurityForm(ModelForm):
    class Meta:
        model = Security
        fields = ['symbol', 'currency', 'exchange', 'isindex', 'list_date']


class UpdateSecurityListDateForm(ModelForm):
    class Meta:
        model = Security
        fields = ['list_date']


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
            cleaned_data.get('industry') == self.last.name):
            msg = u"Nothing changed"
            self.add_error(None, msg)

        return cleaned_data

    class Meta:
        model = SecurityInfo
        fields = ['security', 'valid_date', 'name', 'industry']