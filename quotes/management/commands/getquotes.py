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
        # TODO add more info for add_argument
        parser.add_argument('quoter', help='choose which quoter to get quotes from')
        parser.add_argument('--start', nargs=1, help='start date')
        parser.add_argument('--end', nargs=1, help='end date')
        parser.add_argument('--exchange', nargs=1, help='exchange')
        # TODO add argument for specifying a subset of securities to update

    def handle(self, *args, **options):
        self.stdout.write('Getting quotes for {} from {}\nFrom {} to {}'.format(
            options['exchange'][0], options['quoter'], options['start'][0], options['end'][0]))

        if options['exchange'][0].lower() == 'all':
            all_secs = Security.objects.all()
        else:
            exchanges = options['exchange'][0].split(',')
            qexp = Q(exchange=exchanges[0])
            for i, ex in enumerate(exchanges):
                if i == 0:
                    continue
                qexp |= Q(exchange=ex)

            all_secs = Security.objects.filter(qexp)

        count = 0
        for sec in all_secs:
            data = {'start': options['start'][0],
                    'end': options['end'][0],
                    'mode': 'append',
                    'quoter': options['quoter']}
            form = QuotesForm(data=data, security=sec)
            if form.is_valid():
                count += 1
                form.save()
                self.stdout.write('{}/{}'.format(count, all_secs.count()))
            else:
                logger.debug(data)

        self.stdout.write('Get quotes for {} securities'.format(count))
