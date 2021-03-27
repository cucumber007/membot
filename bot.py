import json

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext


def send_notification(user, lexem):
    pass


class Bot:
    main_keyboard = [
        [InlineKeyboardButton("Show commands", callback_data='show_commands'), ],
    ]
    main_markup = InlineKeyboardMarkup(main_keyboard)

    commands_keyboard = [
        [InlineKeyboardButton("Stats", callback_data='stats'), ],
    ]
    commands_markup = InlineKeyboardMarkup(commands_keyboard)

    def run(self):
        with open("local-properties.json", "r") as f:
            token = json.loads(f.read())["token"]
        updater = Updater(token=token, use_context=True)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(MessageHandler(filters=Filters.text, callback=self.message))
        dispatcher.add_handler(CallbackQueryHandler(self.button))

        # dispatcher.add_error_handler(self.handle_error)

        updater.start_polling()

    def start(self, update, context):
        try:
            # res = requests.post("http://127.0.0.1:8000/password/")
            update.message.reply_text("Hi", reply_markup=self.main_markup)
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
        query.answer()
        if query.data == "show_commands":
            query.message.reply_text("Commands:", reply_markup=self.commands_markup)
        # query.edit_message_text(text=f"Selected option: {query.data}")


bot = Bot()
bot.run()
