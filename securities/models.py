from django.db import models
from django.core.urlresolvers import reverse

from core.utils import build_link


class Security(models.Model):
    """
    The Security model is used to represent a security that can be
    traded on some market.
    """
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    currency = models.CharField(max_length=10, default='')
    quoter = models.CharField(max_length=20, blank=True)
    isindex = models.BooleanField(default=False)

    def __str__(self):
        return "{}({})".format(self.name, self.symbol)

    def __repr__(self):
        return "Security(name={},symbol={},currency={},quoter={},index={}".format(
            self.name, self.symbol, self.currency, self.quoter, self.isindex
        )

    def get_absolute_url(self):
        return reverse('securities:detail', args=[self.id])

    def __str__(self):
        return "{}({})".format(self.name, self.symbol)

    def as_t(self):
        return "<td>{symbol}</td>" \
                "<td>{name}</td>" \
                "<td>{currency}</td>" \
                "<td>{del_link}</td>" \
                "<td>{update_link}</td>" \
                "<td>{quote_link}</td>".format(
                symbol=build_link(reverse('securities:detail', args=[self.id]), self.symbol),
                name=self.name, currency=self.currency,
                del_link=build_link(reverse('securities:del', args=[self.id]), 'Del'),
                update_link=build_link(reverse('securities:update', args=[self.id]), 'Update'),
                quote_link=build_link(reverse('quotes:get', args=[self.id]), 'Quote'),
        )

    def as_p(self):
        return str(self)