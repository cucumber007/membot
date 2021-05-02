import re
from _md5 import md5

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from membot_app import models, serializers, interactor
from membot_app.interactor import get_user, strip_not_none, is_russian


@api_view(http_method_names=["POST"])
def on_lexem_received(request):
    data = request.POST
    user = get_user(request)
    text = data["text"]
    if "//" in text:
        context = text.split("//")[-1]
        rest = "//".join(text.split("//")[:-1])
    else:
        context = None
        rest = text
    parts = re.split('--|—| - | -|- ', rest)
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
        lexem = models.Lexem(user=user, english=strip_not_none(english), russian=strip_not_none(russian),
                             context=strip_not_none(context))
        lexem.save()
        return Response(status=200, data=f"Lexem added: {str(lexem)}")


@api_view(http_method_names=["POST"])
def set_password(request):
    data = request.POST
    user = get_user(request)
    user.password_hash = md5(data["password"])
    user.save()
    return Response(status=200)


@api_view(http_method_names=["POST"])
def trigger_notifications(request):
    data = request.POST
    telegram_id = data.get("telegram_id")
    return interactor.notify_users(telegram_id)


@api_view(http_method_names=["POST"])
def mark(request):
    data = request.POST
    telegram_id = data.get("telegram_id")
    lexem_id = int(data["lexem_id"])
    mem = models.Memorization.objects.get(lexem_id=lexem_id)
    mark_remembered = data["state"] == "mark_remembered"

    interactor.mark(telegram_id, mem, mark_remembered)

    return Response(status=200)


@api_view(http_method_names=["POST"])
def stats(request):
    data = request.POST
    user = get_user(request)
    lexems = models.Lexem.objects.all()[:10]
    edit_queue = models.EditQueueItem.objects.all()[:10]
    mem = models.Memorization.objects.all().order_by("notify_at")[:10]
    return Response(status=200, data={
        "lexems_quantity": len(lexems),
        "edit_queue_size": len(edit_queue),
        "next_word_notification": mem[0].notify_at.strftime("%b %d, %H:%M"),
    })


@api_view(http_method_names=["POST"])
def backup(request):
    data = request.POST
    user = get_user(request)
    lexems = models.Lexem.objects.filter(user=user)
    edit_queue = models.EditQueueItem.objects.filter(user=user)
    mems = models.Memorization.objects.filter(user=user)

    ser = serializers.BackupSerializer({
        "lexems": lexems,
        "edit_queue": edit_queue,
        "memorizations": mems,
    })

    return Response(status=200, data=JSONRenderer().render(ser.data))



