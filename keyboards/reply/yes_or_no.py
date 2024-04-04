from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def yes_or_no() -> ReplyKeyboardMarkup:
    """Функция для перехода к следующему шагу(по большей части пустышка)"""
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('Да'))
    # markup.add(KeyboardButton('Нет'))
    return markup
