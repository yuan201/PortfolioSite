import datetime as dt
import logging

from django.core.management.base import BaseCommand
from django.db.models import Q

from securities.models import Security
from quotes.models import Quote

from securities.models import Security
from quotes.forms import QuotesForm

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Get quote from specified quoter'

    def add_arguments(self, parser):
        parser.add_argument('quoter',)
        parser.add_argument('--start', nargs=1)
        parser.add_argument('--end', nargs=1)

    def handle(self, *args, **options):
        self.stdout.write('Getting quotes from {}\nFrom {} to {}'.format(
            options['quoter'], options['start'][0], options['end'][0]))

        all_secs = Security.objects.filter(Q(exchange='SSE') | Q(exchange='SZSE'))

        count = 0
        for sec in all_secs:
            data = {'start': options['start'][0],
                    'end': options['end'][0],
                    'mode': '1',
                    'quoter': options['quoter']}
            form = QuotesForm(data=data, security=sec)
            if form.is_valid():
                count += 1
                form.save()
                self.stdout.write('{}/{}'.format(count, all_secs.count()))
            else:
                logger.debug(data)

        self.stdout.write('Get quotes for {} securities'.format(count))
