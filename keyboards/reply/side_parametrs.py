from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def range_price() -> ReplyKeyboardMarkup:
    """Функция позволяет выбрать дополнительные параметры при поиске"""
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('Указать диапазон цен'))
    return markup
