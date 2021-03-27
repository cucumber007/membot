from django.db import models
from django.db.models import CASCADE


class User(models.Model):
    telegram_id = models.CharField(max_length=64)
    telegram_username = models.CharField(max_length=64)
    password_hash = models.CharField(max_length=64, null=True, blank=True)


class Lexem(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    english = models.TextField(null=True, blank=True)
    russian = models.TextField(null=True, blank=True)
    context = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.context:
            return f"{self.english} // {self.context} -- {self.russian}"
        else:
            return f"{self.english} -- {self.russian}"


class EditQueueItem(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    raw = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.raw


