from datetime import timedelta

from django.utils import timezone
from rest_framework.response import Response

import bot
from membot_app import models

START_TIME = 10
END_TIME = 24


def notify_users(telegram_id):
    if not telegram_id:
        users = models.User.objects.all()
    else:
        users = models.User.objects.filter(telegram_id=telegram_id)

    lexems = list(models.Lexem.objects.filter(memorization__notify_at__lte=timezone.now()))
    for user in users:
        if should_trigger_notification(user):
            lexems_to_update = list(filter(lambda x: x.user.id == user.id, lexems))
            if lexems_to_update:
                bot.send_lexem_notification(user, lexems_to_update[0])
                user.last_notification = timezone.now()
                user.save()
            elif telegram_id:
                bot.send_message(telegram_id, "No words for you yet")
        elif is_debug(user):
            bot.send_message(telegram_id, f"No time for notification yet: {user.get_next_notification().astimezone(get_timezone(user))}")
    return Response(status=200)


def should_trigger_notification(user):
    user_local_dt = user.last_notification.astimezone(get_timezone(user))
    print(user_local_dt)
    in_time_window = 24 > user_local_dt.hour > 10
    return timezone.now() > user.get_next_notification() and in_time_window


def get_timezone(user):
    return timezone.get_fixed_timezone(timedelta_from_seconds(user.timezone_offset_seconds))


def is_debug(user):
    return user.telegram_username == "spqrta"


def timedelta_to_seconds(td):
    return td.days * 86400 + td.seconds


def timedelta_from_seconds(sec):
    return timedelta(sec / 86400)
