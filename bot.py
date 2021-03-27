import json

import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


class Bot:

    def run(self):
        with open("local-properties.json", "r") as f:
            token = json.loads(f.read())["token"]
        updater = Updater(token=token, use_context=True)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(MessageHandler(filters=Filters.text, callback=self.message))

        # dispatcher.add_error_handler(self.handle_error)

        updater.start_polling()

    def start(self, update, context):
        try:
            # res = requests.post("http://127.0.0.1:8000/password/")
            update.message.reply_text("Hi")
        except Exception as e:
            update.message.reply_text("Error: " + str(e))


    def message(self, update, context):
        try:
            res = requests.post("http://127.0.0.1:8000/message_hook/", {
                "telegram_id": update.effective_user.id,
                "telegram_username": update.effective_user.username,
                "text": update.effective_message.text,
            })
            update.message.reply_text(res.text)
        except Exception as e:
            update.message.reply_text("Error: " + str(e))


bot = Bot()
bot.run()
