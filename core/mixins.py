class TitleHeaderMixin(object):
    def get_context_data(self, **kwargs):
        context = super(TitleHeaderMixin, self).get_context_data(**kwargs)
        context['title'] = self.title
        context['header'] = self.header
        return context
