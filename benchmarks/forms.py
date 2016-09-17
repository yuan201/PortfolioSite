from django import forms

from .models import BenchmarkConstitute, Benchmark
from securities.models import Security


class ConstituteCreateForm(forms.Form):
    name_symbol = forms.CharField(label='Security Name or Symbol', max_length=50)
    percent = forms.FloatField(min_value=0)

    def __init__(self, **kwargs):
        self.benchmark = kwargs.pop('benchmark')
        self.security = None
        super(ConstituteCreateForm, self).__init__(**kwargs)

    def clean(self):
        cleaned_data = super(ConstituteCreateForm, self).clean()
        name_symbol = cleaned_data.get('name_symbol')

        if Security.objects.filter(name=name_symbol).count() == 1:
            self.security = Security.objects.filter(name=name_symbol).first()
        elif Security.objects.filter(symbol=name_symbol).count() == 1:
            self.security = Security.objects.filter(symbol=name_symbol).first()
        else:
            msg = u"Can't find the security specified"
            self.add_error('name_symbol', msg)
            return cleaned_data

        if self.benchmark.constitutes.filter(security=self.security):
            msg = u"Security Already in the Benchmark"
            self.add_error('name_symbol', msg)
            return cleaned_data

    def save_constitute(self):
        BenchmarkConstitute.objects.create(
            security=self.security,
            percent=self.cleaned_data.get('percent'),
            benchmark=self.benchmark,
        )
