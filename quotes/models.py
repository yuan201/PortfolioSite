from django.db import models

from core.types import PositiveDecimalField
from securities.models import Security


class Quote(models.Model):
    """
    In this app, only close quote is used.
    """
    security = models.ForeignKey(Security)
    date = models.DateField()
    open = PositiveDecimalField()
    close = PositiveDecimalField()
    high = PositiveDecimalField()
    low = PositiveDecimalField()
    volume = PositiveDecimalField()


