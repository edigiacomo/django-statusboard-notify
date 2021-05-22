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
