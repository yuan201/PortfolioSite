from django.forms import ModelForm

from .models import Security, SecurityInfo


class NewSecurityForm(ModelForm):
    class Meta:
        model = Security
        fields = ['symbol', 'currency', 'quoter', 'isindex']


class NewSecurityInfoForm(ModelForm):
    # todo update valid info and throw away invalid ones instead of reject everything
    class Meta:
        model = SecurityInfo
        fields = ['security', 'valid_date', 'name', 'industry', 'total_shares', 'outstanding_shares',
                  'list_date']
