from datetime import timedelta

from django.utils import timezone
from rest_framework.response import Response

from membot_app.utils import format_datetime
from telegram_bot import bot
from membot_app import models

START_TIME = 10
END_TIME = 24


def give_me_the_word(user):
    lexems = get_lexems_for_notification(user=user)
    return send_the_word(user, lexems, manual=True)


def send_the_word(user, lexems_to_update, manual):
    if lexems_to_update:
        bot.send_lexem_notification(user, lexems_to_update[0])
        user.last_notification = timezone.now()
        user.save()
    elif manual:
        bot.send_message(user.telegram_id, "No words for you yet")


def notify_users(telegram_id):
    if not telegram_id:
        users = models.User.objects.all()
    else:
        users = models.User.objects.filter(telegram_id=telegram_id)

    lexems = get_lexems_for_notification(user=None)
    for user in users:
        if should_trigger_notification(user, manual=(telegram_id is not None)):
            lexems_to_update = list(filter(lambda x: x.user.id == user.id, lexems))
            send_the_word(user, lexems_to_update, manual=False)

    return Response(status=200)


def get_lexems_for_notification(user):
    res = models.Lexem.objects \
        .filter(memorization__notify_at__lte=timezone.now()) \
        .filter(russian__isnull=False) \
        .filter(english__isnull=False)

    if user:
        res = res.filter(user=user)
    return list(res)


def should_trigger_notification(user, manual=False):
    user_local_dt = timezone.now().astimezone(user.get_timezone())
    print(user_local_dt)
    in_time_window = END_TIME > user_local_dt.hour > START_TIME
    is_time = timezone.now() > user.get_next_notification()
    res = is_time and in_time_window
    if not res and is_debug(user) and manual:
        if not in_time_window:
            bot.send_message(
                user.telegram_id,
                f"Not in time window: {format_datetime(user_local_dt)} ({START_TIME}-{END_TIME})"
            )
        if not is_time:
            dt = format_datetime(user.get_next_notification().astimezone(user.get_timezone()))
            bot.send_message(
                user.telegram_id,
                f"No time for notification yet: {dt}"
            )
    return res


def mark(telegram_id, mem, mark_remembered):
    if mark_remembered:
        plus_days = get_plusdays_for_next_stage(mem.interval_stage)
        mem.notify_at = timezone.now() + timedelta(days=plus_days)
        mem.interval_stage += 1
        mem.save()
        bot.send_message(telegram_id, f"I'll reask you in {plus_days} days")
    else:
        mem.interval_stage = 0
        mem.notify_at = timezone.now()
        mem.save()
        bot.send_message(telegram_id, f"Memorization value of this word has been reset")


def get_stats(user):
    lexems = models.Lexem.objects.filter(user=user).all()
    memorizations = models.Memorization.objects.filter(user=user).all()

    total_lexems_quantity = lexems.count()

    stages = {}
    max_interval_stage = memorizations.order_by("-interval_stage").first().interval_stage
    if max_interval_stage is None:
        max_interval_stage = 0
    for i in range(0, max_interval_stage):
        count = lexems.filter(memorization__interval_stage=i).count()
        stages[i] = count

    edit_queue = models.EditQueueItem.objects.count()

    data = {
        "total_lexems_quantity": total_lexems_quantity,
        "stages": stages,
        "edit_queue_size": edit_queue,
        "next_notification": format_datetime(user.get_next_notification().astimezone(user.get_timezone())),
    }

    mem = memorizations.order_by("notify_at").first()
    if mem:
        data["next_word_notification"] = format_datetime(mem.notify_at)
    print(data)
    return Response(status=200, data=data)


def is_debug(user):
    return user.telegram_username in ["spqrta", "alinamanulova"]


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
        return s.lower().strip()
    else:
        return s


def get_plusdays_for_next_stage(prev_stage):
    if prev_stage < 0:
        return 0
    res = {
        0: 1,
        1: 2,
        2: 14,
        3: 60,
    }.get(prev_stage)
    if res is None:
        res = 60
    return res


def show_answer(user, lexem_id, message_id):
    lexem = models.Lexem.objects.filter(id=lexem_id).first()
    bot.set_lexem_state_open(user, lexem, message_id)
