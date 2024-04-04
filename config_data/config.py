import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

DATABASE_PATH = "database/database.sql"
BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_URL = "https://hotels4.p.rapidapi.com/v2/get-meta-data"
RAPID_API_KEY = os.getenv("RAPID_API_KEY")

RAPID_API_HEADERS = {
    "X-RapidAPI-Key": RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

RAPID_API_ENDPOINTS = {
    "cities": "https://hotels4.p.rapidapi.com/locations/v3/search",
    "hotels": "https://hotels4.p.rapidapi.com/properties/v2/list",
    "hotel_details": "https://hotels4.p.rapidapi.com/properties/v2/detail"
}

DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Вывести справку"),
    ("low", "Запросить минимальные значения"),
    ("high", "Запросить максимальные значения"),
    ("custom", "Запросить диапазон значений"),
    ("history", "Узнать историю запросов")
)
