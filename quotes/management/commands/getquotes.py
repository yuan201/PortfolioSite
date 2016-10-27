from django.core.management.base import BaseCommand

from securities.models import Security
from quotes.models import Quote


class Command(BaseCommand):
    help = 'Get quote from specified quoter'

    def add_arguments(self, parser):
        #parser.add_argument('quoter',)
        pass
