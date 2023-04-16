# encoding: utf-8
from io import StringIO

from django.test import TestCase
from django.conf import settings
from django.core import mail
from django.core.management import call_command
from django.utils.translation import gettext as _


from statusboard.models import Service, ServiceGroup, SERVICE_STATUSES

from statusboard_notify.models import Notification, Recipient
from statusboard_notify.utils import (
    send_notification_mail,
    render_notification_telegram,
)


class TestUtils(TestCase):
    def test_send_notification_mail(self):
        s = Service(name="test", status=0)
        s.save()
        s.status = 2
        s.save()
        notifications = Notification.objects.all()
        send_notification_mail(notifications)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(len(mail.outbox), len(settings.STATUSBOARD_NOTIFY_EMAIL_RECIPIENTS))
        # Controlla che per ogni mail ci sia almeno un destinatario
        for m in mail.outbox:
            self.assertTrue(len(m.to) > 0)

    def test_render_notification_telegram(self):
        s = Service(name="test", status=0)
        s.save()
        s.status = 2
        s.save()
        n = Notification.objects.first()
        msg = render_notification_telegram(n)
        self.assertEqual(
            msg,
            "\U0001F7E0 **{}** changed from __{}__ to __{}__".format(
                s.name,
                n.get_from_status_display(),
                n.get_to_status_display(),
            )
        )
        with self.settings(
            LANGUAGE_CODE="it",
            USE_L10N=True,
            USE_I18N=True,
        ):
            n = Notification.objects.first()
            msg = render_notification_telegram(n)
            self.assertEqual(
                msg,
                "\U0001F7E0 **{}** è passato da __{}__ a __{}__".format(
                    s.name,
                    n.get_from_status_display(),
                    n.get_to_status_display(),
                )
            )


class TestCommand(TestCase):
    def test_send_notifications(self):
        s = Service(name="test", status=0)
        s.save()
        s.status = 2
        s.save()

        out = StringIO()

        self.assertEqual(len(mail.outbox), 0)
        call_command('send_notifications', stdout=out)
        self.assertEqual(len(mail.outbox), len(settings.STATUSBOARD_NOTIFY_EMAIL_RECIPIENTS))
        self.assertTrue(_(SERVICE_STATUSES[2][1]) in mail.outbox[0].body)
        notifications = Notification.objects.all()
        self.assertEqual(notifications.count(), 0)


class TestRecipient(TestCase):
    def setUp(self):
        self.s1 = Service(name="test1", status=0)
        self.s1.save()
        self.s1.status = 2
        self.s1.save()

        self.s2 = Service(name="test2", status=0)
        self.s2.save()
        self.s2.status = 0
        self.s2.save()

        self.r = Recipient(email="ciccio@riccio.com")
        self.r.save()
        self.r.services.add(self.s1)
        self.r.save()

    def test_recipient_notifications(self):
        self.assertEqual(self.r.notifications().count(), 1)
        self.assertEqual(self.r.notifications().first().service, self.s1)

    def test_send_notification_mail(self):
        with self.settings(STATUSBOARD_NOTIFY_EMAIL_RECIPIENTS=[]):
            self.assertEqual(Notification.objects.all().count(), 1)
            send_notification_mail(Notification.objects.all())
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].to, ["ciccio@riccio.com"])
            self.assertTrue("test1" in mail.outbox[0].body)
            self.assertFalse("test2" in mail.outbox[0].body)

    def test_send_notification_mail_command(self):
        out = StringIO()
        with self.settings(STATUSBOARD_NOTIFY_EMAIL_RECIPIENTS=[]):
            self.assertEqual(Notification.objects.all().count(), 1)
            call_command('send_notifications', stdout=out)
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].to, ["ciccio@riccio.com"])
            self.assertTrue("test1" in mail.outbox[0].body)
            self.assertFalse("test2" in mail.outbox[0].body)
            self.assertEqual(Notification.objects.all().count(), 0)

    def test_send_notification_mail_command_dry_run(self):
        out = StringIO()
        with self.settings(STATUSBOARD_NOTIFY_EMAIL_RECIPIENTS=[]):
            self.assertEqual(Notification.objects.all().count(), 1)
            call_command('send_notifications', '--dry-run', stdout=out)
            self.assertEqual(len(mail.outbox), 0)
            self.assertEqual(Notification.objects.all().count(), 1)

    def test_send_notification_mail_empty_recipient(self):
        r = Recipient(email="ciccio2@riccio.com")
        r.save()
        r.services.add(self.s2)
        r.save()
        with self.settings(STATUSBOARD_NOTIFY_EMAIL_RECIPIENTS=[]):
            # Controlla che venga mandata una mail ma non al destinatario
            # ciccio2@riccio.com, perché non è associato a servizi per cui
            # avviene la notifica via email
            self.assertEqual(Notification.objects.all().count(), 1)
            send_notification_mail(Notification.objects.all())
            self.assertEqual(len(mail.outbox), 1)
            self.assertNotEqual(mail.outbox[0].to, ["ciccio2@riccio.com"])
