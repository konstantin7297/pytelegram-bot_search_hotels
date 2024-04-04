from telebot.types import Message
from loader import bot


@bot.message_handler(state=None)
def bot_echo(message: Message):
    """Функция, куда попадает любой не используемый в боте текст"""
    bot.reply_to(message, "Эхо без состояния или фильтра.\n" f"Сообщение: {message.text}")
