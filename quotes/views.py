import logging

from django.shortcuts import render
from django.views.generic import FormView
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from .forms import QuotesForm
from securities.models import Security
from core.mixins import TitleHeaderMixin

logger = logging.getLogger('quotes_view')

