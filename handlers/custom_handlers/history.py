from loader import bot
from telebot.types import Message
from database.database import get_db
import urllib
import ast


def helper(message: Message, hotels):
    """Вспомогательная функция для вывода истории полученных по запросу отелей"""
    bot.send_message(message.from_user.id, 'Результат поиска:')
    result = [hotels[1:-1]]
    for index, hotel in enumerate(result):
        hotel = ast.literal_eval(hotel)
        photo = open('photo.jpg', 'wb')
        photo_map = open('photo_map.jpg', 'wb')
        photo.write(urllib.request.urlopen(hotel['photo']).read())
        photo_map.write(urllib.request.urlopen(hotel['static_photo']).read())
        photo.close()
        photo_map.close()

        bot.send_message(
            message.from_user.id,
            f'Найденный отель №{index + 1}:\n'
            f'Название: {hotel["name"]}\n'
            f'Полный адрес: {hotel["address"]}\n'
            f'Цена: {hotel["price"]}\n'
            f'Ссылка на сайт: https://www.hotels.com/h{hotel["id"]}.Hotel-Information'
        )
        photo = open('photo.jpg', 'rb')
        photo_map = open('photo_map.jpg', 'rb')
        bot.send_message(message.from_user.id, 'Фото отеля:')
        bot.send_photo(message.from_user.id, photo)
        bot.send_message(message.from_user.id, 'Местонахождение отеля на карте:')
        bot.send_photo(message.from_user.id, photo_map)
        photo.close()
        photo_map.close()


@bot.message_handler(commands=["history"])
def bot_history(message: Message):
    """Функция достает из базы данных таблицу истории запросов и выводит пользователю последние несколько запросов с его id"""
    tasks = get_db(message)
    bot.send_message(message.from_user.id, 'Вот ваши последние 10 запросов:')

    if len(tasks) > 10:
        for task in tasks[-10:]:
            bot.send_message(message.from_user.id, f'Запрос: {task.title} \nДата: {task.date} \nВремя: {task.time}')
            if task.hotels:
                helper(message, task.hotels)

    elif len(tasks) <= 10:
        for task in tasks:
            bot.send_message(message.from_user.id, f'Запрос: {task.title} \nДата: {task.date} \nВремя: {task.time}')
            if task.hotels:
                helper(message, task.hotels)
    else:
        bot.send_message(message.from_user.id, 'Ничего нет')
