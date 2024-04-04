from telebot.types import Message
from config_data.config import DEFAULT_COMMANDS
from loader import bot
from database.database import logger


@bot.message_handler(commands=["help"])
@logger
def bot_help(message: Message):
    """Функция выводит все имеющиеся команды бота пользователю"""
    text = [f"/{command} - {desk}" for command, desk in DEFAULT_COMMANDS]
    bot.reply_to(message, "\n".join(text))
