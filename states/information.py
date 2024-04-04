from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    """Класс состояний пользователя"""
    side_status = State()
    status = State()
    side_city = State()
    city = State()
    city_id = State()
    command = State()
    hotels_count = State()
    data_in = State()
    data_out = State()
    min_price = State()
    max_price = State()




