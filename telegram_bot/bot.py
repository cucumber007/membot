import json
from datetime import timedelta

import requests
import telegram

from django.utils import timezone
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.error import BadRequest
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext

from membot import settings
from telegram_bot import keyboards, button_handlers
from telegram_bot.formatters import LexemFormatter


def send_lexem_notification(user, lexem):
    bot.tg_bot.send_message(chat_id=user.telegram_id, text=LexemFormatter(lexem).hidden_state(),
                            reply_markup=keyboards.lexem.markup)


def set_lexem_state_open(user, lexem, message_id):
    bot.tg_bot.edit_message_text(chat_id=user.telegram_id, text=LexemFormatter(lexem).open_state(),
                                 message_id=message_id,
                                 reply_markup=keyboards.lexem_open.markup)


def send_message(telegram_id, text):
    bot.tg_bot.send_message(chat_id=telegram_id, text=text)


class Bot:
    def __init__(self):
        print("Run bot")
        self.tg_bot = None

    def run(self):
        try:
            with open("local-properties.json", "r") as f:
                token = json.loads(f.read())["token"]
                updater = Updater(token=token, use_context=True)
                dispatcher = updater.dispatcher
                self.tg_bot = updater.bot
                dispatcher.add_handler(CommandHandler("start", self.start))
                dispatcher.add_handler(CommandHandler("trigger_notifications", self.trigger_notifications))
                dispatcher.add_handler(MessageHandler(filters=Filters.text, callback=self.message))
                dispatcher.add_handler(CallbackQueryHandler(self.button))

                # dispatcher.add_error_handler(self.handle_error)

                updater.start_polling()
        except FileNotFoundError:
            print("token not found")

    def start(self, update, context):
        try:
            # res = requests.post("http://127.0.0.1:8000/password/")
            update.message.reply_text(
                f"""
                Hi. 
                \nUse '<phrase> -- <phrase> // <context>' format to add items
                \nAdmin: {settings.ADMIN_URL}" 
                \nCommands:
                \n/trigger_notifications
                """,
                reply_markup=keyboards.main.markup)
        except Exception as e:
            update.message.reply_text("Error: " + str(e), reply_markup=keyboards.main.markup)

    def trigger_notifications(self, update, context):
        try:
            requests.post("http://127.0.0.1:8000/api/trigger_notifications/", {
                "telegram_id": update.effective_user.id,
            })
        except Exception as e:
            update.message.reply_text("Error: " + str(e), reply_markup=keyboards.main.markup)

    def message(self, update, context):
        try:
            res = requests.post("http://127.0.0.1:8000/api/message_hook/", {
                "telegram_id": update.effective_user.id,
                "telegram_username": update.effective_user.username,
                "text": update.effective_message.text,
            })
            update.message.reply_text(res.text, reply_markup=keyboards.main.markup)
        except Exception as e:
            update.message.reply_text("Error: " + str(e), reply_markup=keyboards.main.markup)

    def button(self, update, *args):
        try:
            query = update.callback_query
            try:
                query.answer()
            except BadRequest as e:
                if "Query is too old" in str(e):
                    pass
                else:
                    raise e

            button_handlers.handle(update, query)

            # query.edit_message_text(text=f"Selected option: {query.data}")
        except Exception as e:
            text = "Error: " + str(e)
            if len(text) > 1024:
                text = text[:1024]
            update.effective_message.reply_text(text, reply_markup=keyboards.main.markup)


bot = Bot()
bot.run()
