import datetime, functools
from peewee import *
from typing import Callable, Optional
from telebot.types import Message
from config_data.config import DATABASE_PATH


db = SqliteDatabase(DATABASE_PATH)


def logger(_func: Optional[Callable] = None) -> Callable:
    """Функция-декоратор собирает данные и заносит их в датабазу"""
    def function(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            set_db(*args, **kwargs)
            result = func(*args, **kwargs)
            return result

        return wrapped_func

    if _func is None:
        return function
    else:
        return function(_func)


def set_db(message: Message, command=None, result=None) -> None:
    """Функция для создания и заполнения базы данных"""
    try:
        date, time = str(datetime.datetime.now()).split()
        time = time.split('.')
        act_user = User.get(user_id=message.from_user.id)
        if command:
            print(f'User[{message.from_user.id}]: command: {command}, hotels: {result} date: {date}, time: {time[0]}')
            Task(user=act_user, title=command, hotels=result, date=date, time=time[0]).save()

        else:
            print(f'User[{message.from_user.id}]: command: {message.text}, date: {date}, time: {time[0]}')
            Task(user=act_user, title=message.text, hotels=None, date=date, time=time[0]).save()
    except:
        pass


def get_db(message: Message):
    """Функция для получения задач от пользователя"""
    act_user = User.get(user_id=message.from_user.id)
    tasks = [task for task in Task.select().where(Task.user == act_user)]
    return tasks


class BaseModel(Model):
    """Базовый класс связывающий дочерние классы с файлом датабазы"""
    class Meta:
        database = db


class User(BaseModel):
    """Класс пользователя, регистрирует пользователя"""
    user_id = IntegerField(primary_key=True)
    username = CharField()
    first_name = CharField()
    last_name = CharField(null=True)


class Task(BaseModel):
    """Класс задачи, хранит информацию о задаче и пользователе, запросившим ее"""
    user = ForeignKeyField(User)
    title = CharField()
    hotels = CharField()
    date = CharField()
    time = CharField()
