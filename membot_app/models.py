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
        return f"{self.english} // {self.context} -- {self.russian}"


class EditQueue(models.Model):
    raw = models.TextField()
    old = models.ForeignKey(Lexem, on_delete=CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
