import os
from typing import Type

import requests
import re

TAG_RE = re.compile(r'<[^>]+>')


def remove_tags(text):
    return TAG_RE.sub('', text)


url = "https://hotels4.p.rapidapi.com/locations/search"
headers = {
    'x-rapidapi-key': os.getenv("API_KEY"),
    'x-rapidapi-host': "hotels4.p.rapidapi.com"
    }


def get_city(city: str) -> dict or str:
    """
    Функция, которая реализует поиск города через запрос к Api.
    Выводит словарь где ключ это id города, а значение это название города
    :param city: str
    :return: dict or str
    """
    locale = 'ru_RU' if re.match(r'[А-Яа-яЁё]+', city) else 'en_US'
    city = city.capitalize()
    querystring = {"query": city, "locale": locale}
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = response.json()
    if response.status_code != 200:
        return 'Простите, я не могу найти информацию по отелям в этом городе. Свяжитесь с оператором'
    if data["moresuggestions"] == 0:
        return 'Произошла ошибка,\n'\
               'Попробуйте снова:\n1) Введите навание города на русском языке.\n' \
               '2) Убедитесь что город введен верно\n' \
               'Например: Москва\n' \
               '3) Кликните на нужный вариант'
    else:
        return {
            item['destinationId']:remove_tags(item["caption"]) for item in data["suggestions"][0]["entities"]
            if item['type'] == 'CITY' and item['name'] == city}
