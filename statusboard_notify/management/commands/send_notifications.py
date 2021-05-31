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

    def add_arguments(self, parser):
        parser.add_argument('-n', '--dry-run', action="store_true")

    def handle(self, *args, **kwargs):
        notifications = Notification.objects.all()
        if not notifications.exists():
            self.stdout.write("Notification queue is empty")
            return

        for dest, func in (
            ("telegram", send_notification_telegram),
            ("email", send_notification_mail),
        ):
            self.stdout.write("Sending {} notifications via {}".format(
                notifications.count(),
                dest,
            ))
            if not kwargs["dry_run"]:
                try:
                    func(notifications)
                except Exception as e:
                    self.stderr.write(e)

        self.stdout.write("Removing {} notifications from the queue".format(
            notifications.count()
        ))
        if not kwargs["dry_run"]:
            try:
                notifications.delete()
            except Exception as e:
                self.stderr.write(e)
