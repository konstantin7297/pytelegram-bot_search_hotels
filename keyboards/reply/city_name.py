from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Message
from loader import bot
from handlers.custom_handlers.all_requests import requests_menu


def city_name(message: Message) -> ReplyKeyboardMarkup:
    """Функция для уточнения существования введенного города"""
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['city'] = message.text
        result = requests_menu(data, mode='city_check')

        if result:
            data['city'] = result
            markup = ReplyKeyboardMarkup()
            markup.add(KeyboardButton(result))
            return markup

        else:
            data['city'] = ''
            raise ValueError
