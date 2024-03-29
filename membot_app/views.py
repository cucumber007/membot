import json
import re
from _md5 import md5

# Create your views here.
from django.db.models import Q
from django.views.generic import TemplateView
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from membot_app import models, serializers, interactor
from membot_app.interactor import get_user, strip_not_none, is_russian
from membot_app.utils import decrypt


@api_view(http_method_names=["POST"])
def on_lexem_received(request):
    data = request.POST
    user = get_user(request)
    text = data["text"]
    english, russian, context = interactor.parse_lexem(text)
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
def give_me_the_word(request):
    user = get_user(request)
    return interactor.give_me_the_word(user)


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
    user = get_user(request)
    return interactor.get_stats(user)


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


@api_view(http_method_names=["POST"])
def show_answer(request):
    data = request.POST
    user = get_user(request)
    lexem_id = data["lexem_id"]
    message_id = data["message_id"]
    interactor.show_answer(user, lexem_id, message_id)
    return Response(status=200)


class EditQueueView(TemplateView):
    template_name = "edit_queue.html"

    def get(self, request, *args, **kwargs):
        self.data = json.loads(decrypt(request.GET["p"]))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data'] = self.data
        user = interactor.get_user_by_telegram_id(self.data["telegram_id"])
        context['user'] = user
        res = []
        edit_queue_items = models.EditQueueItem.objects.filter(user=user).all()
        for eq in edit_queue_items:
            lexems = interactor.get_lexems_for_edit_queue(eq)
            res.append([eq, lexems])
        context['edit_queue_data'] = res
        return context
