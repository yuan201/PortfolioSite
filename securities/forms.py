from django.forms import ModelForm

from .models import Security, SecurityInfo


class NewSecurityForm(ModelForm):

    class Meta:
        model = Security
        fields = ['symbol', 'currency', 'quoter', 'isindex']


class NewSecurityInfoForm(ModelForm):

    class Meta:
        model = SecurityInfo
        fields = ['security', 'valid_date', 'name', 'industry', 'total_shares', 'outstanding_shares',
                  'list_date']