from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from loader import bot
from telebot.types import Message, CallbackQuery
from datetime import date, timedelta
from states.information import UserInfoState


def ru_word(sym):
    """Вспомогательная функция для русификации календаря"""
    if sym == 'y':
        return 'год'
    elif sym == 'm':
        return 'месяц'
    elif sym == 'd':
        return 'день'


def get_calendar(is_process=False, callback_data=None, **kwargs):
    """Функция создания и обновления календаря"""
    if is_process:
        result, key, step = DetailedTelegramCalendar(calendar_id=kwargs['calendar_id'],
                                                     current_date=kwargs.get('current_date'),
                                                     min_date=kwargs['min_date'],
                                                     max_date=kwargs['max_date'],
                                                     locale=kwargs['locale']).process(callback_data.data)
        return result, key, step

    else:
        calendar, step = DetailedTelegramCalendar(calendar_id=kwargs['calendar_id'],
                                                  current_date=kwargs.get('current_date'),
                                                  min_date=kwargs['min_date'],
                                                  max_date=kwargs['max_date'],
                                                  locale=kwargs['locale']).build()
        return calendar, step


def start(message: Message) -> None:
    """Функция для начала работы с календарем"""
    today = date.today()
    calendar, step = DetailedTelegramCalendar(calendar_id=1, current_date=today, min_date=today, max_date=today + timedelta(days=365), locale="ru").build()
    bot.set_state(message.from_user.id, UserInfoState.data_in, message.chat.id)
    bot.send_message(message.from_user.id, f"Выберите {ru_word(step) if LSTEP[step] else LSTEP[step]}", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def survey(call: CallbackQuery):
    """Функция для взаимодействия с календарем и сохранения даты заезда"""
    today = date.today()
    result, key, step = get_calendar(calendar_id=1, current_date=today, min_date=today, max_date=today + timedelta(days=365), locale="ru", is_process=True,
                                     callback_data=call)

    if not result and key:
        bot.edit_message_text(f"Выберите {ru_word(step) if LSTEP[step] else LSTEP[step]}", call.message.chat.id, call.message.message_id, reply_markup=key)

    elif result:
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            year, month, day = str(result).split('-')
            data['check_in'] = result
            data['day_in'] = int(day)
            data['month_in'] = int(month)
            data['year_in'] = int(year)
            bot.edit_message_text(f"Вы указали (гггг-мм-дд): {result}", call.message.chat.id, call.message.message_id)

            bot.send_message(call.from_user.id, "Укажите дату выезда")
            calendar, step = get_calendar(calendar_id=2, min_date=result + timedelta(days=1), max_date=result + timedelta(days=365), locale="ru")
            bot.send_message(call.from_user.id, f"Выберите {ru_word(step) if LSTEP[step] else LSTEP[step]}", reply_markup=calendar)
            bot.set_state(call.from_user.id, UserInfoState.data_out, call.message.chat.id)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def handle_departure_date(call: CallbackQuery):
    """Функция для взаимодействия с календарем и сохранения даты выезда"""
    today = date.today()
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        result, key, step = get_calendar(calendar_id=2,
                                         current_date=today,
                                         min_date=data['check_in'] + timedelta(days=1),
                                         max_date=data['check_in'] + timedelta(days=365),
                                         locale="ru",
                                         is_process=True,
                                         callback_data=call)

    if not result and key:
        bot.edit_message_text(f"Выберите {ru_word(step) if LSTEP[step] else LSTEP[step]}",
                              call.from_user.id,
                              call.message.message_id,
                              reply_markup=key)

    elif result:
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            year, month, day = str(result).split('-')
            data['check_in'] = result
            data['day_out'] = int(day)
            data['month_out'] = int(month)
            data['year_out'] = int(year)
            bot.edit_message_text(f"Вы указали (гггг-мм-дд): {result}", call.message.chat.id, call.message.message_id)

            bot.set_state(call.from_user.id, UserInfoState.hotels_count, call.message.chat.id)
            bot.send_message(call.from_user.id, 'Введите количество отелей (максимум: 5)')
