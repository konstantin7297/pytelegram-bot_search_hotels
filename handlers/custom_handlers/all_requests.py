from config_data.config import RAPID_API_ENDPOINTS, RAPID_API_HEADERS
from typing import Collection, Dict, Any
import requests


def search_collection(collection: Collection, data, mode, index=None, info_list=None) -> None:
    """Вспомогательная функция для работы с вложенными коллекциями"""
    if isinstance(collection, dict):
        for key in collection.keys():
            if isinstance(collection[key], (dict, list, tuple)):
                search_info(collection[key], data, mode, index, info_list)

    elif isinstance(collection, (list, tuple)):
        for i_elem in collection:
            if isinstance(i_elem, (dict, list, tuple)):
                search_info(i_elem, data, mode, index, info_list)


def search_info(collection: Collection, data, mode, index=None, info_list=None) -> Any:
    """Функция сбора нужной информации с реквестов"""
    if mode == 'city':
        if isinstance(collection, dict):
            if 'type' in collection.keys() and collection['type'] == 'CITY' and 'gaiaId' in collection.keys():
                info_list.append(collection['gaiaId'])
            else:
                search_collection(collection, data=data, mode=mode, index=index, info_list=info_list)
        elif isinstance(collection, list):
            search_collection(collection, data=data, mode=mode, index=index, info_list=info_list)

        if len(info_list) > 0:
            return f"{info_list[0]}"
        else:
            return None

    elif mode == 'city_check':
        if isinstance(collection, dict):
            if 'shortName' in collection.keys():
                info_list.append(collection['shortName'])
            else:
                search_collection(collection, data=data, mode=mode, index=index, info_list=info_list)
        elif isinstance(collection, list):
            search_collection(collection, data=data, mode=mode, index=index, info_list=info_list)

        if len(info_list) > 0:
            return f"{info_list[0]}"
        else:
            return None

    elif mode == 'hotels':
        if isinstance(collection, dict) and 'properties' in collection.keys():
            for index, i_elem in enumerate(collection['properties']):
                info_list.append(dict())
                if i_elem['id']:
                    info_list[index]['id'] = i_elem['id']
                if i_elem['name']:
                    info_list[index]['name'] = i_elem['name']
                if i_elem['propertyImage']['image']['url']:
                    info_list[index]['photo'] = i_elem['propertyImage']['image']['url']
                if i_elem['price']['lead']['amount'] and i_elem['price']['lead']['currencyInfo']['code']:
                    info_list[index]['price'] = str(i_elem['price']['lead']['amount']) + ' ' + \
                                                       i_elem['price']['lead']['currencyInfo']['code'] + ' ' + \
                                                       i_elem['price']['priceMessages'][0]['value']
                    info_list[index]['classic_price'] = int(i_elem['price']['lead']['amount'])
                if i_elem['star']:
                    info_list[index]['star'] = i_elem['star']
        else:
            search_collection(collection, data=data, mode=mode, index=index, info_list=info_list)

    elif mode == 'hotel':
        if isinstance(collection, dict) and 'location' in collection.keys():
            if collection['location']['address']['addressLine']:
                info_list[index]['address'] = collection['location']['address']['addressLine']
            if collection['location']['staticImage']['url']:
                info_list[index]['static_photo'] = collection['location']['staticImage']['url']
        else:
            search_collection(collection, data=data, mode=mode, index=index, info_list=info_list)


def response_func(data, mode, my_id=None) -> Dict:
    """Функция для запроса реквеста по заданным параметрам"""
    if mode == 'city':
        requests_mode = 'GET'
        endpoint = RAPID_API_ENDPOINTS['cities']
        headers = RAPID_API_HEADERS
        params = {f"q": data['city'], "locale": "en_US", "langid": "1033", "siteid": "300000001"}

    elif mode == 'hotels':
        if data['command'] == '/custom':
            min_price = data['min_price']
            max_price = data['max_price']
            sort = "PRICE_LOW_TO_HIGH"

        elif data['command'] == '/low':
            min_price = 25
            max_price = 200
            sort = "PRICE_LOW_TO_HIGH"

        elif data['command'] == '/high':
            min_price = 25
            max_price = 200
            sort = "PRICE_HIGH_TO_LOW"
        else:
            min_price = 25
            max_price = 200
            sort = "PRICE_LOW_TO_HIGH"

        requests_mode = 'POST'
        endpoint = RAPID_API_ENDPOINTS['hotels']
        headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPID_API_HEADERS["X-RapidAPI-Key"],
        "X-RapidAPI-Host": RAPID_API_HEADERS["X-RapidAPI-Host"]
    }

        params = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": { "regionId": my_id },
        "checkInDate": {
            "day": data['day_in'],
            "month": data['month_in'],
            "year": data['year_in']
        },
        "checkOutDate": {
            "day": data['day_out'],
            "month": data['month_out'],
            "year": data['year_out']
        },
        "rooms": [
            {
                "adults": 2,
                "children": [{ "age": 5 }, { "age": 7 }]
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": data['hotels_count'],
        "sort": sort,
        "filters": { "price": {
            "max": max_price,
            "min": min_price
        } }
    }

    elif mode == 'hotel':
        requests_mode = 'POST'
        endpoint = RAPID_API_ENDPOINTS["hotel_details"]
        headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPID_API_HEADERS["X-RapidAPI-Key"],
        "X-RapidAPI-Host": RAPID_API_HEADERS["X-RapidAPI-Host"]
    }
        params = {
            "currency": "USD",
            "eapid": 1,
            "locale": "en_US",
            "siteId": 300000001,
            "propertyId": my_id
        }

    if requests_mode == 'GET':
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()

    elif requests_mode == 'POST':
        response = requests.post(endpoint, json=params, headers=headers)
        if response.status_code == 200:
            return response.json()


def requests_menu(data: Dict, mode=None) -> Any:
    """Функция-меню, которая принимает информацию от пользователя и направляет ее на обработку в остальные функции"""
    try:
        if mode == 'city_check':
            city_dict = response_func(data=data, mode='city')
            data['city_dictor'] = city_dict
            check_city = list()
            result = search_info(data['city_dictor'], data=data, mode='city_check', info_list=check_city)
            if result:
                return result
            else:
                return None

        elif not mode:
            id_cities = list()
            id_city = search_info(data['city_dictor'], data=data, mode='city', info_list=id_cities)

            if id_city:
                hotels_info_list = list()
                hotels_dict = response_func(data=data, mode='hotels', my_id=id_city)
                search_info(hotels_dict, data=data, mode='hotels', info_list=hotels_info_list)

                if len(hotels_info_list) > 0:
                    hotel_id_list = [hotel['id'] for hotel in hotels_info_list]
                    for index, hotel_id in enumerate(hotel_id_list):
                        hotel_dict = response_func(data=data, mode='hotel', my_id=hotel_id)
                        search_info(hotel_dict, data=data, mode='hotel', index=index, info_list=hotels_info_list)
                    return hotels_info_list
    except IndexError:
        return None
