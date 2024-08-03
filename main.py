import handlers
from telebot.custom_filters import StateFilter

from loader import bot
from database.database import db, User, Task
from utils.set_bot_commands import set_default_commands


if __name__ == "__main__":
    db.create_tables([User, Task])
    bot.add_custom_filter(StateFilter(bot))
    set_default_commands(bot)
    bot.infinity_polling()

