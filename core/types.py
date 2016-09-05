from decimal import getcontext

from django.db import models
from django.core.validators import ValidationError

PREC = getcontext().prec
MAXD = PREC + 10


def positive_validator(value):
    if value < 0:
        raise ValidationError(_('Negative value'), code='negative')


class PositiveDecimalField(models.DecimalField):
    default_validators = [positive_validator]

    def __init__(self, *args, **kwargs):
        super(PositiveDecimalField, self).__init__(*args, **kwargs)
        self.max_digits = MAXD
        self.decimal_places = PREC
