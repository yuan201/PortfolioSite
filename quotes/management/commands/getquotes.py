import datetime as dt

from django.core.management.base import BaseCommand

from securities.models import Security
from quotes.models import Quote

from securities.models import Security
from quotes.forms import QuotesForm


class Command(BaseCommand):
    help = 'Get quote from specified quoter'

    def add_arguments(self, parser):
        parser.add_argument('quoter',)
        parser.add_argument('--start', nargs=1)
        parser.add_argument('--end', nargs=1)

    def handle(self, *args, **options):
        self.stdout.write('Getting quotes from {}\nFrom {} to {}'.format(
            options['quoter'], options['start'][0], options['end'][0]))

        all_secs = Security.objects.filter(quoter=options['quoter'])

        count = 0
        for sec in all_secs:
            data = {'start': options['start'][0],
                    'end': options['end'][0],
                    'mode': '1'}
            form = QuotesForm(data=data, security=sec)
            if form.is_valid():
                count += 1
                form.save()
                self.stdout.write('.', ending='')
            else:
                self.stdout.write(form.errors)

        self.stdout.write('Get quotes for {} securities'.format(count))
