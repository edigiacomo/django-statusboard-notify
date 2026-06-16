from django import template

from statusboard_notify.utils import get_notification_status_emoji

register = template.Library()


@register.filter
def statusboard_notify_status_emoji(notification):
    return get_notification_status_emoji(notification)
