import re
from _md5 import md5

from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

import bot
from membot_app import models


@api_view(http_method_names=["POST"])
def on_message_received(request):
    data = request.POST
    user = get_user(request)
    text = data["text"]
    if "//" in text:
        context = text.split("//")[-1]
        rest = "//".join(text.split("//")[:-1])
    else:
        context = None
        rest = text
    parts = re.split('\--|—', rest)
    if len(parts) == 2:
        part1 = parts[0]
        part2 = parts[1]
        if is_russian(part1):
            russian = part1
            english = part2
        else:
            russian = part2
            english = part1
    else:
        part = "--".join(parts)
        if is_russian(part):
            russian = part
            english = None
        else:
            english = part
            russian = None
    existant_rus, existant_eng = None, None
    if russian:
        existant_rus = list(models.Lexem.objects.filter(russian=russian, user=user))
    if english:
        existant_eng = list(models.Lexem.objects.filter(english=english, user=user))
    if existant_rus or existant_eng:
        models.EditQueueItem(user=user, raw=text).save()
        return Response(status=200, data=f"Already have such item, added to edit queue")
    else:
        lexem = models.Lexem(user=user, english=strip_not_none(english), russian=strip_not_none(russian), context=strip_not_none(context))
        lexem.save()
        return Response(status=200, data=f"Lexem added: {str(lexem)}")


@api_view(http_method_names=["POST"])
def set_password(request):
    data = request.POST
    user = get_user(request)
    user.password_hash = md5(data["password"])
    user.save()
    return Response(status=200)


@api_view(http_method_names=["GET"])
def trigger_notifications(request):
    users = models.User.objects.all()
    lexems = list(models.Lexem.objects.filter(memorization__notify_at__lte=timezone.now()))
    for user in users:
        lexem = map(lambda x: x.user.id == user.id, lexems).__next__()
        if lexem:
            bot.send_notification(user, lexem)
    return Response(status=200)


def get_user(request):
    data = request.POST
    user = models.User.objects.filter(telegram_id=data["telegram_id"]).first()
    if not user:
        user = models.User(
            telegram_id=data["telegram_id"],
            telegram_username=data["telegram_username"]
        )
        user.save()
    return user


def is_russian(s):
    for i in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя":
        if i in s:
            return True
    return False


def strip_not_none(s):
    if s:
        return s.strip()
    else:
        return s
