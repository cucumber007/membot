from _md5 import md5

from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response

from membot_app import models


@api_view(http_method_names=["POST"])
def on_message_received(request):
    data = request.POST
    user = get_user(request)
    text = data["text"]
    context = text.split("//")[-1]
    rest = "//".join(text.split("//")[:-1])
    parts = rest.split("--")
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
    lexem = models.Lexem(user=user, english=english, russian=russian, context=context)
    lexem.save()
    return Response(status=200, data=f"Lexem added: {str(lexem)}")


@api_view(http_method_names=["POST"])
def set_password(request):
    data = request.POST
    user = get_user(request)
    user.password_hash = md5(data["password"])
    user.save()
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

