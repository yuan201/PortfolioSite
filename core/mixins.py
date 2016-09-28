from portfolios.models import Portfolio


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

