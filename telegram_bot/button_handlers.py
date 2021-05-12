import json

import requests
import telegram

from membot import settings
from membot_app import interactor
from membot_app.utils import format_underscore
from telegram_bot import keyboards


def show_commands(update, query):
    query.message.reply_text("Commands:", reply_markup=keyboards.commands.markup)


def give_me_the_word(update, query):
    requests.post("http://127.0.0.1:8000/api/give_me_the_word/", {
        "telegram_id": update.effective_user.id,
    })


def stats(update, query):
    res = requests.post("http://127.0.0.1:8000/api/stats/", {
        "telegram_id": update.effective_user.id,
    })
    message = ""
    data = json.loads(res.text)
    total_lexems_quantity = data["total_lexems_quantity"]
    for k, v in data.items():
        if k == "stages":
            for stage, sv in v.items():
                stage = int(stage)
                message += f"\t{stage} ({interactor.get_plusdays_for_next_stage(stage - 1)} d) - {round(sv / float(total_lexems_quantity) * 100)} %\n"
        else:
            message += f"{format_underscore(k)}: {v}\n"

    # formatted = json.dumps(, indent=4, ensure_ascii=False)
    query.message.reply_text(f"```\n{message} ```", parse_mode=telegram.ParseMode.MARKDOWN_V2)


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


def edit_lexem(update, query):
    lexem_id = update.effective_message.text.split("|")[0]
    query.message.reply_text(settings.ADMIN_URL+f"membot_app/lexem/{lexem_id}/change/")


handlers = {
    "show_commands": show_commands,
    "give_me_the_word": give_me_the_word,
    "stats": stats,
    "backup": backup,
    "show_answer": show_answer,
    "mark_remembered": mark,
    "mark_forgotten": mark,
    "url": url,
    "edit_lexem": edit_lexem,
}


def handle(update, query):
    handler = handlers.get(query.data)
    if handler:
        handler(update, query)
    else:
        raise Exception(f"No handler for '{query.data}' button")
