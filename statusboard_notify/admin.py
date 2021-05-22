from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Recipient


class RecipientAdmin(admin.ModelAdmin):
    list_display = ('email', 'service_list')

    def service_list(self, o):
        return ", ".join(s.name for s in o.services.all())
    service_list.short_description = _('service list')


admin.site.register(Recipient, RecipientAdmin)
