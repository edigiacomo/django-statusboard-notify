# Copyright (C) 2021 Emanuele Di Giacomo <emanuele@digiacomo.cc>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

import pypandoc

try:
    telegram = None
    import telegram
except ImportError:
    pass


from .models import Recipient


def send_notification_mail_for_recipients(recipients, notifications):
    # Se non ci sono notifiche, non invio la mail
    if not notifications.exists():
        return

    try:
        sender = settings.STATUSBOARD_NOTIFY_EMAIL_SENDER
    except AttributeError:
        return

    html_msg, plain_msg = render_notification_message(notifications)

    try:
        subject = settings.STATUSBOARD_NOTIFY_EMAIL_SUBJECT
    except:
        subject = _("[statusboard] Service status updates")

    for recipient in recipients:
        send_mail(subject, plain_msg, sender, [recipient],
                  fail_silently=False, html_message=html_msg)


def send_notification_mail(notifications):
    try:
        send_notification_mail_for_recipients(
            settings.STATUSBOARD_NOTIFY_EMAIL_RECIPIENTS,
            notifications,
        )
    except AttributeError:
        pass

    for recipient in Recipient.objects.all():
        send_notification_mail_for_recipients(
            [recipient.email],
            recipient.notifications(notifications),
        )


def render_notification_message(notifications):
    html_msg = render_to_string('statusboard_notify/email.html', {
        'notifications': notifications,
    })
    plain_msg = pypandoc.convert_text(html_msg, "markdown_strict",
                                      format="html")
    return html_msg, plain_msg


def send_notification_telegram(notifications):
    if not telegram:
        pass

    try:
        token = settings.STATUSBOARD_NOTIFY_TELEGRAM_TOKEN
        chat_id = settings.STATUSBOARD_NOTIFY_TELEGRAM_CHAT_ID
    except AttributeError:
        return

    bot = telegram.Bot(token=token)
    for notification in notifications:
        bot.send_message(chat_id=chat_id,
                         text=render_notification_telegram(notification),
                         parse_mode=telegram.ParseMode.MARKDOWN)


def render_notification_telegram(notification):
    status_emoji = {
        "0": "\U0001F7E2",  # 🟢
        "1": "\U0001F535",  # 🔵
        "2": "\U0001F7E0",  # 🟠
        "3": "\U0001F534",  # 🔴
    }
    msg = _(
        "%(emoji)s **%(name)s** changed from __%(fromst)s__ to __%(tost)s__"
    ) % {
        'emoji': status_emoji.get(str(notification.to_status)),
        'name': notification.service.name,
        'fromst': notification.get_from_status_display(),
        'tost': notification.get_to_status_display(),
    }
    return msg
