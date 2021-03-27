import json

import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


class Bot:

    def run(self):
        with open("local-properties.json", "r") as f:
            token = json.loads(f.read())["token"]
        updater = Updater(token=token, use_context=True)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", self.message))
        dispatcher.add_handler(MessageHandler(filters=Filters.text, callback=self.message))

        # dispatcher.add_error_handler(self.handle_error)

        updater.start_polling()

    def message(self, update, context):
        try:
            requests.post("http://127.0.0.1/message_hook")
            print("sent")
        except Exception as e:
            update.message.reply_text("Ошибочка: " + str(e))


bot = Bot()
bot.run()
