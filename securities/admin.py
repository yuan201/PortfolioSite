from django.contrib import admin

from .models import Security, SecurityInfo


@admin.register(Security)
class SecurityAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'currency', 'quoter', 'no_quotes', 'isindex', 'list_date')
    search_fields = ['symbol']
    ordering = ['symbol']
    list_filter = ['isindex', 'list_date']


@admin.register(SecurityInfo)
class SecurityInfoAdmin(admin.ModelAdmin):
    list_display = ('security', 'name', 'valid_date', 'industry')
    search_fields = ['name', 'industry']
    ordering = ['-valid_date']

