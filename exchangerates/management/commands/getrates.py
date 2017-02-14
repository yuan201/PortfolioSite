from django.core.management.base  import BaseCommand

from exchangerates.models import ExchangeRate


class Command(BaseCommand):
    help = 'Get Exchange Rates from OpenExchangeRates'

    def handle(self, *args, **options):
        self.stdout.write('Getting exchange rates')

        ExchangeRate.update_db()

