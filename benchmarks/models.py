import logging

from django.db import models

from core.types import PositiveDecimalField
from securities.models import Security

logger = logging.getLogger(__name__)


class Benchmark(models.Model):
    """
    A benchmark is different from a portfolio in 
    """