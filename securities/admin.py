from django.contrib import admin

from .models import Security, SecurityInfo


class SecurityAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'currency', 'quoter', 'isindex')
    search_fields = ['symbol', 'isindex']
    ordering = ['symbol']


class SecurityInfoAdmin(admin.ModelAdmin):
    list_display = ('security', 'name', 'valid_date', 'industry', 'total_shares', 'outstanding_shares',
                    'list_date')
    search_fields = ['name', 'industry']
    ordering = ['-valid_date']

admin.site.register(Security, SecurityAdmin)
admin.site.register(SecurityInfo, SecurityInfoAdmin)
