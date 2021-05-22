from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

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

    html_msg, plain_msg = render_notification_message(notifications)

    from_email = "statuspage <statuspage@smr.arpa.emr.it>"
    subject = "[statuspage] Aggiornamento dello stato dei servizi"
    for recipient in recipients:
        send_mail(subject, plain_msg, from_email, [recipient],
                  fail_silently=False, html_message=html_msg)


def send_notification_mail(notifications):
    send_notification_mail_for_recipients(
        settings.STATUS_EMAIL_NOTIFY_RECIPIENTS,
        notifications,
    )

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
        token = getattr(settings, "STATUS_EMAIL_TELEGRAM_TOKEN")
        chat_id = getattr(settings, "STATUS_EMAIL_TELEGRAM_CHAT_ID")
    except AttributeError:
        return

    status_emoji = {
        "0": "\U0001F7E2",  # 🟢
        "1": "\U0001F535",  # 🔵
        "2": "\U0001F7E0",  # 🟠
        "3": "\U0001F534",  # 🔴
    }

    bot = telegram.Bot(token=token)
    for notification in notifications:
        msg = "{} {} è passato da {} a {}".format(
            status_emoji.get(str(notification.to_status)),
            notification.service.name,
            notification.get_from_status_display(),
            notification.get_to_status_display(),
        )
        bot.send_message(chat_id=chat_id,
                         text=msg,
                         parse_mode=telegram.ParseMode.MARKDOWN)
