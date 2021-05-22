# encoding: utf-8
from django.test import TestCase
from django.conf import settings
from django.core import mail
from django.core.management import call_command
from django.utils.translation import gettext as _
from django.utils.six import StringIO


from statusboard.models import Service, ServiceGroup, SERVICE_STATUSES

from .models import Notification, Recipient
from .utils import send_notification_mail


class TestUtils(TestCase):
    def test_send_notification_mail(self):
        s = Service(name="test", status=0)
        s.save()
        s.status = 2
        s.save()
        notifications = Notification.objects.all()
        send_notification_mail(notifications)
        self.assertEquals(Notification.objects.count(), 1)
        self.assertEquals(len(mail.outbox), len(settings.STATUS_EMAIL_NOTIFY_RECIPIENTS))
        # Controlla che per ogni mail ci sia almeno un destinatario
        for m in mail.outbox:
            self.assertTrue(len(m.to) > 0)


class TestCommand(TestCase):
    def test_send_notifications(self):
        s = Service(name="test", status=0)
        s.save()
        s.status = 2
        s.save()

        out = StringIO()

        self.assertEquals(len(mail.outbox), 0)
        call_command('send_notifications', stdout=out)
        self.assertEquals(len(mail.outbox), len(settings.STATUS_EMAIL_NOTIFY_RECIPIENTS))
        self.assertTrue(_(SERVICE_STATUSES[2][1]) in mail.outbox[0].body)
        notifications = Notification.objects.all()
        self.assertEquals(notifications.count(), 0)


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
        self.assertEquals(self.r.notifications().count(), 1)
        self.assertEquals(self.r.notifications().first().service, self.s1)

    def test_send_notification_mail(self):
        from .utils import send_notification_mail
        with self.settings(STATUS_EMAIL_NOTIFY_RECIPIENTS=[]):
            self.assertEquals(Notification.objects.all().count(), 1)
            send_notification_mail(Notification.objects.all())
            self.assertEquals(len(mail.outbox), 1)
            self.assertEquals(mail.outbox[0].to, ["ciccio@riccio.com"])
            self.assertTrue("test1" in mail.outbox[0].body)
            self.assertFalse("test2" in mail.outbox[0].body)

    def test_send_notification_mail_command(self):
        out = StringIO()
        with self.settings(STATUS_EMAIL_NOTIFY_RECIPIENTS=[]):
            self.assertEquals(Notification.objects.all().count(), 1)
            call_command('send_notifications', stdout=out)
            self.assertEquals(len(mail.outbox), 1)
            self.assertEquals(mail.outbox[0].to, ["ciccio@riccio.com"])
            self.assertTrue("test1" in mail.outbox[0].body)
            self.assertFalse("test2" in mail.outbox[0].body)
            self.assertEquals(Notification.objects.all().count(), 0)

    def test_send_notification_mail_empty_recipient(self):
        from .utils import send_notification_mail
        r = Recipient(email="ciccio2@riccio.com")
        r.save()
        r.services.add(self.s2)
        r.save()
        with self.settings(STATUS_EMAIL_NOTIFY_RECIPIENTS=[]):
            # Controlla che venga mandata una mail ma non al destinatario
            # ciccio2@riccio.com, perché non è associato a servizi per cui
            # avviene la notifica via email
            self.assertEquals(Notification.objects.all().count(), 1)
            send_notification_mail(Notification.objects.all())
            self.assertEquals(len(mail.outbox), 1)
            self.assertNotEquals(mail.outbox[0].to, ["ciccio2@riccio.com"])
