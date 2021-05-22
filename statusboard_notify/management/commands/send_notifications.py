from django.core.management.base import BaseCommand

from statusboard_notify.models import Notification
from statusboard_notify.utils import send_notification_mail
from statusboard_notify.utils import send_notification_telegram


class Command(BaseCommand):
    help = "Send statusbord notifications"
    leave_locale_alone = True

    def add_arguments(self, parser):
        parser.add_argument('-n', '--dry-run', action="store_true")

    def handle(self, *args, **kwargs):
        notifications = Notification.objects.all()
        if not notifications.exists():
            return
        elif kwargs["dry_run"]:
            self.stdout.write("Invierei la notifica per {} eventi".format(
                notifications.count()
            ))
            self.stdout.write("Eliminerei {} eventi".format(
                notifications.count()
            ))
        else:
            try:
                send_notification_telegram(notifications)
            except Exception as e:
                self.stderr.write(e)

            try:
                send_notification_mail(notifications)
            except Exception as e:
                self.stderr.write(e)

            self.stdout.write("Inviata la notifica per {} eventi".format(
                notifications.count()
            ))
            self.stdout.write("Eliminazione di {} eventi".format(
                notifications.count()
            ))
            notifications.delete()
