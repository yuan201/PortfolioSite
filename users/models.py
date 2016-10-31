from django.db import models
from django.conf import settings

LANGUAGES = [('CN', 'Chinese'), ('EN', 'English')]
QUOTERS = [('Tushare', 'Tushare'), ('Local', 'Local')]


class UserSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    language = models.CharField(max_length=2, choices=LANGUAGES, default='EN')
    quoter = models.CharField(max_length=10, choices=QUOTERS, default='Local')
