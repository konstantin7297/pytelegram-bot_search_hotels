from telebot.types import Message
from peewee import IntegrityError
from loader import bot
from database.database import User


@bot.message_handler(commands=["start"])
def bot_start(message: Message):
    """Стартовая функция при работе с ботом. Помогает пользователю адаптироваться при начале работы"""
    try:
        User.create(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        ).save()
        act_user = User.get(user_id=message.from_user.id)
        bot.reply_to(message, f"Привет, {act_user.first_name}! Можешь использовать команду /help чтобы освоиться.")

    except IntegrityError:
        act_user = User.get(user_id=message.from_user.id)
        bot.reply_to(message, f"Рад вас снова видеть, {act_user.first_name}!")
