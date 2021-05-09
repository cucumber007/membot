from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class Keyboard:

    def __init__(self, buttons) -> None:
        super().__init__()
        self.buttons = buttons
        self.markup = InlineKeyboardMarkup(buttons)


main = Keyboard([
    [InlineKeyboardButton("Show commands", callback_data='show_commands')]
])

lexem = Keyboard(main.buttons + [ [
    InlineKeyboardButton("Show answer", callback_data='show_answer'),
    InlineKeyboardButton("Mark as forgotten", callback_data='mark_forgotten'),
]])

lexem_open = Keyboard(main.buttons + [ [
    InlineKeyboardButton("Mark as remembered", callback_data='mark_remembered'),
    InlineKeyboardButton("Mark as forgotten", callback_data='mark_forgotten'),
]])


# lexem = Keyboard(lexem_keyboard)

lexem_keyboard = [[
        InlineKeyboardButton("Mark as remembered", callback_data='mark_remembered'),
        InlineKeyboardButton("Mark as forgotten", callback_data='mark_forgotten'),
    ], ]


commands = Keyboard([[
    InlineKeyboardButton("Give me the word!", callback_data='trigger_notifications'),
    InlineKeyboardButton("Stats", callback_data='stats'),
    InlineKeyboardButton("Backup", callback_data='backup'),
    InlineKeyboardButton("Admin URL", callback_data='url'),
]])
