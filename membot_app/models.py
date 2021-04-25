from django.db import models
from django.db.models import CASCADE
from django.utils import timezone


class User(models.Model):
    telegram_id = models.CharField(max_length=64)
    telegram_username = models.CharField(max_length=64)
    password_hash = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return self.telegram_username


class Lexem(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    english = models.TextField(null=True, blank=True)
    russian = models.TextField(null=True, blank=True)
    context = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        Memorization(user=self.user, lexem=self, interval_stage=0, notify_at=timezone.now()).save()

    def __str__(self):
        if self.context is not None:
            return f"{self.english} // {self.context} -- {self.russian}"
        else:
            return f"{self.english} -- {self.russian}"


class EditQueueItem(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    raw = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.raw


class Memorization(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    lexem = models.ForeignKey(Lexem, on_delete=CASCADE)
    interval_stage = models.IntegerField()
    notify_at = models.DateTimeField()



