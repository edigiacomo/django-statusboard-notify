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
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

from statusboard.models import Service, SERVICE_STATUSES


class Recipient(models.Model):
    """Recipient for the notifications. Each recipient can receive
    notifications for a subset of services."""
    email = models.EmailField(unique=True, verbose_name="email")
    services = models.ManyToManyField(Service, verbose_name=_("services"))

    def notifications(self, qs=None):
        if qs is None:
            qs = Notification.objects.all()

        return qs.filter(service__in=self.services.all())

    class Meta:
        verbose_name = _('recipient')
        verbose_name_plural = _('recipients')


class Notification(models.Model):
    """Pending notifications."""
    service = models.OneToOneField(Service, on_delete=models.deletion.CASCADE)
    from_status = models.IntegerField(choices=SERVICE_STATUSES, null=True, blank=True)
    to_status = models.IntegerField(choices=SERVICE_STATUSES)

    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')


@receiver(post_save, sender=Service)
def update_notification(sender, instance, **kwargs):
    """Update the state of a pending notification. A status change from
    "operational" to "performance issues" (or viceversa) is ignored.
    The notification is removed when a service status changes to operational or
    "performance issues". The pending notification keeps track of the first and
    last status: if the service status changes again before the notification is
    sent, this function overwrites the final status.
    """
    if any([
        instance._status == instance.status,
        (instance._status, instance.status) in ((0, 1), (1, 0))
    ]):
        # Ignore if the status is unchanged or the change is between 0
        # (operational) and 1 (performance issues).
        return
    else:
        try:
            n = Notification.objects.get(service=instance)
            if n.from_status == instance.status:
                # If the notification exists and the new final status is equals
                # to the starting status of the notification, remove it.
                n.delete()
            else:
                # Else, update the final status.
                n.to_status = instance.status
                n.save()
        except Notification.DoesNotExist:
            # Create the notification if it doesn't exist.
            n = Notification(service=instance, from_status=instance._status,
                             to_status=instance.status)
            n.save()
