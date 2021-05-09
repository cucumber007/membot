import json

import requests
import telegram

from membot import settings
from telegram_bot import keyboards


def show_commands(update, query):
    query.message.reply_text("Commands:", reply_markup=keyboards.commands.markup)


def trigger_notifications(update, query):
    requests.post("http://127.0.0.1:8000/api/trigger_notifications/", {
        "telegram_id": update.effective_user.id,
    })


def stats(update, query):
    res = requests.post("http://127.0.0.1:8000/api/stats/", {
        "telegram_id": update.effective_user.id,
    })
    query.message.reply_text(res.text)


def backup(update, query):
    res = requests.post("http://127.0.0.1:8000/api/backup/", {
        "telegram_id": update.effective_user.id,
    })
    if res.status_code != 200:
        raise Exception(res.text)
    data = json.loads(res.text[1:-1].replace('\\"', '"'))
    datas = json.dumps(data, indent=4)
    query.message.reply_text(f"```{datas}```", parse_mode=telegram.ParseMode.MARKDOWN_V2)


def show_answer(update, query):
    res = requests.post("http://127.0.0.1:8000/api/show_answer/", {
        "telegram_id": update.effective_user.id,
        "message_id": update.effective_message.message_id,
        "lexem_id": update.effective_message.text.split("|")[0],
    })
    if res.status_code != 200:
        raise Exception(res.text)


def mark(update, query):
    requests.post("http://127.0.0.1:8000/api/mark/", {
        "telegram_id": update.effective_user.id,
        "lexem_id": update.effective_message.text.split("|")[0],
        "state": query.data
    })


def url(update, query):
    query.message.reply_text(settings.ADMIN_URL)


handlers = {
    "show_commands": show_commands,
    "trigger_notifications": trigger_notifications,
    "stats": stats,
    "backup": backup,
    "show_answer": show_answer,
    "mark_remembered": mark,
    "mark_forgotten": mark,
    "url": url,
}


def handle(update, query):
    handler = handlers.get(query.data)
    if handler:
        handler(update, query)
    else:
        raise Exception(f"No handler for '{query.data}' button")
