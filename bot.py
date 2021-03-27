import json

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.error import BadRequest
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext


def send_lexem_notification(user, lexem):
    bot.tg_bot.send_message(chat_id=user.telegram_id, text=f"{lexem.id}|{lexem.english} -- {lexem.russian}",
                            reply_markup=Bot.lexem_markup)


def send_message(telegram_id, text):
    bot.tg_bot.send_message(chat_id=telegram_id, text=text)


class Bot:
    main_keyboard = [
        [InlineKeyboardButton("Show commands", callback_data='show_commands'), ],
    ]
    main_markup = InlineKeyboardMarkup(main_keyboard)

    lexem_keyboard = [[
        InlineKeyboardButton("Mark as remembered", callback_data='mark_remembered'),
        InlineKeyboardButton("Mark as forgotten", callback_data='mark_forgotten'),
    ], ] + main_keyboard
    lexem_markup = InlineKeyboardMarkup(lexem_keyboard)

    commands_keyboard = [
        [
            InlineKeyboardButton("Stats", callback_data='stats'),
            InlineKeyboardButton("Give me the word!", callback_data='trigger_notifications'),
        ],
    ]
    commands_markup = InlineKeyboardMarkup(commands_keyboard)

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
                dispatcher.add_handler(MessageHandler(filters=Filters.text, callback=self.message))
                dispatcher.add_handler(CallbackQueryHandler(self.button))

                # dispatcher.add_error_handler(self.handle_error)

                updater.start_polling()
        except FileNotFoundError:
            print("token not found")

    def start(self, update, context):
        try:
            # res = requests.post("http://127.0.0.1:8000/password/")
            update.message.reply_text("Hi. \n Use '<phrase> -- <phrase> // <context>' format to add items \n Admin: http://membot.sytes.net:8000/admin", reply_markup=self.main_markup)
        except Exception as e:
            update.message.reply_text("Error: " + str(e), reply_markup=self.main_markup)

    def message(self, update, context):
        try:
            res = requests.post("http://127.0.0.1:8000/message_hook/", {
                "telegram_id": update.effective_user.id,
                "telegram_username": update.effective_user.username,
                "text": update.effective_message.text,
            })
            update.message.reply_text(res.text, reply_markup=self.main_markup)
        except Exception as e:
            update.message.reply_text("Error: " + str(e), reply_markup=self.main_markup)

    def button(self, update, *args):
        query = update.callback_query
        try:
            query.answer()
        except BadRequest as e:
            if "Query is too old" in str(e):
                pass
            else:
                raise e

        if query.data == "show_commands":
            query.message.reply_text("Commands:", reply_markup=self.commands_markup)
        if query.data == "trigger_notifications":
            requests.post("http://127.0.0.1:8000/trigger_notifications/", {
                "telegram_id": update.effective_user.id,
            })
        if query.data == "stats":
            res = requests.post("http://127.0.0.1:8000/stats/", {
                "telegram_id": update.effective_user.id,
            })
            query.message.reply_text(res.text)
        if "mark" in query.data:
            requests.post("http://127.0.0.1:8000/mark/", {
                "telegram_id": update.effective_user.id,
                "lexem_id": update.effective_message.text.split("|")[0],
                "state": query.data
            })
        # query.edit_message_text(text=f"Selected option: {query.data}")


bot = Bot()
bot.run()
