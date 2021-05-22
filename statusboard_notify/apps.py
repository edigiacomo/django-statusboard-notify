from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StatusboardNotifyConfig(AppConfig):
    name = 'statusboard_notify'
    verbose_name = _('statusboard notifier')
