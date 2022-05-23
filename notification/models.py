from django.conf import settings
from django.db import models
from django.utils import timezone


class NotificationQuerySet(models.QuerySet):

    def create(self, **kwargs):
        one_minute_ago = timezone.now() - timezone.timedelta(minutes=1)

        notification_already_sent = self.filter(
            created__gte=one_minute_ago,
            **kwargs,
        ).exists()

        if notification_already_sent:
            pass
        else:
            instance = super().create(**kwargs)
            instance.send()
            return instance

    def mine(self, user):
        return self.filter(user=user)

    def unread(self):
        return self.filter(is_read=False)

    def mark_read(self):
        return self.unread().update(is_read=True)


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notifications',
        verbose_name='Users',
        on_delete=models.PROTECT
    )
    data = models.JSONField('Data')
    is_read = models.BooleanField('Read', default=False)
    created = models.DateTimeField('Created', auto_now_add=True)

    objects = NotificationQuerySet.as_manager()

    def mark_as_read(self):
        self.is_read = True
        self.save()