from portfolios.models import Portfolio
from core.utils import last_business_day, next_business_day, to_business_timestamp


class TitleHeaderMixin(object):
    def get_context_data(self, **kwargs):
        context = super(TitleHeaderMixin, self).get_context_data(**kwargs)
        context['title'] = self.title
        context['header'] = self.header
        return context

    def __init__(self):
        self.title = None
        self.header = None


# todo check usage of the following two mixins, if no usage delete
class PortfoliosMixin(object):
    def get_context_data(self, **kwargs):
        context = super(PortfoliosMixin, self).get_context_data(**kwargs)
        context['portfolios'] = Portfolio.objects.all()
        return context


class PortfoliosTestMixin(object):
    def setup_portfolios(self):
        if Portfolio.objects.count() == 0:
            Portfolio.objects.create(name='value')
            Portfolio.objects.create(name='trend')

    def check_all_portfolios_listed(self, response):
        for ptf in Portfolio.objects.all():
            self.assertContains(response, ptf.name)


class AdminFormatMixin(object):
    @staticmethod
    def _format_for_print(value):
        if value:
            return '{:.2f}'.format(value)
        else:
            return ""


class DateUtilMixin(object):
    """
    Date related utilities for models.
    Assuming there is a field called date in the model and the model is sorted on this field
    """
    def first_date(self):
        return to_business_timestamp(self.earliest().date)

    def last_date(self):
        return to_business_timestamp(self.latest().date)

    def append_date(self):
        return self.last_date()+1

    def date_range(self):
        pass

