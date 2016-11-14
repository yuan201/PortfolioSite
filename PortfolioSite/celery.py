import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PortfolioSite.settings')

app = Celery('PortfolioSite')
app.config_from_object('django.conf:settings')

from django.conf import settings
app.autodiscover_tasks(settings.INSTALLED_APPS)
