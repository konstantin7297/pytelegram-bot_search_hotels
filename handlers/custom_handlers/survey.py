import urllib
from database.database import logger, set_db
from telebot.types import Message, ReplyKeyboardRemove
from states.information import UserInfoState
from loader import bot
from keyboards.reply.side_parametrs import range_price
from keyboards.reply.city_name import city_name
from keyboards.reply.calendar import start
from keyboards.reply.yes_or_no import yes_or_no
# from structure_example.handlers.custom_handlers.all_requests import requests_menu
from .all_requests import requests_menu


@bot.message_handler(commands=["low", 'high', 'custom'])
def survey(message: Message):
    """Функция начала опроса, запрашивает у пользователя город и активирует состояние пользователя"""
    bot.set_state(message.from_user.id, UserInfoState.side_city, message.chat.id)
    try:
        bot.send_message(message.from_user.id, 'Введите город для поиска')

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['command'] = message.text
    except:
        bot.send_message(message.from_user.id, "Что-то пошло не так, повторите попытку")
        bot.delete_state(message.from_user.id)


@bot.message_handler(state=UserInfoState.side_city)
def get_city(message: Message) -> None:
    """Функция проверяет на существование введенное название города и возвращает его в случае положительного ответа"""
    bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
    try:
        bot.send_message(message.from_user.id, "Уточните название города:", reply_markup=city_name(message))
    except:
        bot.send_message(message.from_user.id, "Что-то пошло не так, повторите попытку")
        bot.delete_state(message.from_user.id)


@bot.message_handler(state=UserInfoState.city)
def get_date_in(message: Message) -> None:
    """Функция запускает календарь"""
    try:
        bot.send_message(message.from_user.id, 'Укажите дату заезда', reply_markup=ReplyKeyboardRemove())
        start(message)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city'] = message.text
    except:
        bot.send_message(message.from_user.id, "Что-то пошло не так, повторите попытку")
        bot.delete_state(message.from_user.id)


@bot.message_handler(state=UserInfoState.hotels_count)
def set_hotels_count(message: Message) -> None:
    """Промежуточная функция, которая запускает сбор дополнительных параметров в случае необходимости, либо активирует поиск"""
    try:
        if message.text.isdigit() and int(message.text) in range(1, 6):
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['hotels_count'] = int(message.text)

                if data['command'] == '/custom':
                    bot.set_state(message.from_user.id, UserInfoState.side_status, message.chat.id)
                    bot.send_message(message.from_user.id, 'Выберите дополнительный параметр',
                                     reply_markup=range_price())

                elif data['command'] == '/low' or data['command'] == '/high':
                    bot.set_state(message.from_user.id, UserInfoState.status, message.chat.id)
                    bot.send_message(message.from_user.id, 'Начать поиск?', reply_markup=yes_or_no())
        else:
            bot.send_message(message.from_user.id, 'Количество отелей должно быть указано цифрой от 1 до 5')
    except:
        bot.send_message(message.from_user.id, "Что-то пошло не так, повторите попытку")
        bot.delete_state(message.from_user.id)


@bot.message_handler(state=UserInfoState.side_status)
def get_min_price(message: Message) -> None:
    """Функция сбора дополнительных параметров"""
    try:
        if message.text == 'Указать диапазон цен':
            bot.set_state(message.from_user.id, UserInfoState.min_price, message.chat.id)
            bot.send_message(message.from_user.id, 'Введите минимальную цену в USD', reply_markup=ReplyKeyboardRemove())
    except:
        bot.send_message(message.from_user.id, "Что-то пошло не так, повторите попытку")
        bot.delete_state(message.from_user.id)


@bot.message_handler(state=UserInfoState.min_price)
def get_max_price(message: Message) -> None:
    """Функция сбора дополнительных параметров"""
    try:
        if message.text.isdigit():
            bot.set_state(message.from_user.id, UserInfoState.max_price, message.chat.id)
            bot.send_message(message.from_user.id, 'Введите максимальную цену в USD')

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['min_price'] = message.text
        else:
            bot.send_message(message.from_user.id, 'Цена должна быть указана цифрой')
    except:
        bot.send_message(message.from_user.id, "Что-то пошло не так, повторите попытку")
        bot.delete_state(message.from_user.id)


@bot.message_handler(state=UserInfoState.max_price)
def set_max_price(message: Message) -> None:
    """Промежуточная функция, которая после сбора дополнительных параметров запускает поиск"""
    try:
        if message.text.isdigit():
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['max_price'] = message.text

            bot.set_state(message.from_user.id, UserInfoState.status, message.chat.id)
            bot.send_message(message.from_user.id, 'Начать поиск?', reply_markup=yes_or_no())
        else:
            bot.send_message(message.from_user.id, 'Цена должна быть указана цифрой')
    except:
        bot.send_message(message.from_user.id, "Что-то пошло не так, повторите попытку")
        bot.delete_state(message.from_user.id)


@bot.message_handler(state=UserInfoState.status)
def final(message: Message) -> None:
    """Функция отвечающая за поиск отелей по всем собранным параметрам"""
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if data['command'] == '/low' or data['command'] == '/high' or data['command'] == '/custom':

            bot.send_message(message.from_user.id, 'Пожалуйста подождите...', reply_markup=ReplyKeyboardRemove())
            result = requests_menu(data)
            set_db(message, data['command'], result)

            if result:
                try:
                    for index, hotel in enumerate(result):
                        photo = open('photo.jpg', 'wb')
                        photo_map = open('photo_map.jpg', 'wb')
                        photo.write(urllib.request.urlopen(result[index]['photo']).read())
                        photo_map.write(urllib.request.urlopen(result[index]['static_photo']).read())
                        photo.close()
                        photo_map.close()

                        bot.send_message(
                            message.from_user.id,
                            f'Найденный отель №{index + 1}:\n'
                            f'Название: {result[index]["name"]}\n'
                            f'Полный адрес: {result[index]["address"]}\n'
                            f'Цена: {result[index]["price"]}\n'
                            f'Ссылка на сайт: https://www.hotels.com/h{result[index]["id"]}.Hotel-Information'
                        )
                        photo = open('photo.jpg', 'rb')
                        photo_map = open('photo_map.jpg', 'rb')
                        bot.send_message(message.from_user.id, 'Фото отеля:')
                        bot.send_photo(message.from_user.id, photo)
                        bot.send_message(message.from_user.id, 'Местонахождение отеля на карте:')
                        bot.send_photo(message.from_user.id, photo_map)
                        photo.close()
                        photo_map.close()
                except IndexError:
                    pass
            else:
                bot.send_message(message.from_user.id, 'К сожалению ничего не найдено, попробуйте еще раз')
    bot.delete_state(message.from_user.id)
