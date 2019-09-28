# -*- coding: utf-8 -*-
from datetime import datetime

import requests
import re
from bs4 import BeautifulSoup


class AstraMenu:
    def __init__(self):
        self.menu_url = 'http://www.astra-catering.pl/zestaw-dnia.html'
        self.day_of_the_week = datetime.today().weekday()
        self.weekly_menu = list()
        self._get_page()
        self._decode_content()
        self._create_soup_object()
        self._get_tables_from_content()
        self._read_tables()

    def get_todays_menu(self) -> dict:
        if self.day_of_the_week < 5:
            return {'astra_menu': self.weekly_menu[self.day_of_the_week]}
        else:
            return {'astra_menu': ''}

    def _get_page(self):
        self.page = requests.get(self.menu_url)

    def _decode_content(self):
        self.content = self.page.content.decode('utf-8', errors='ignore').replace('&oacute;', 'ó').replace('&nbsp;', '')

    def _create_soup_object(self):
        self.soup = BeautifulSoup(self.content, 'lxml')

    def _get_tables_from_content(self):
        self.tables = self.soup.find_all('table')[:-1]

    def _read_tables(self):
        for table in self.tables:
            day_menu = [x for x in table.text.replace(' :', ': ').split('\n') if x is not '']
            if 'zupa' in day_menu[0].lower() and 'zestaw' in day_menu[1].lower():
                day_menu = day_menu[0].split(" ", 1) + day_menu[1:]
            for word in day_menu:
                if day_menu.index(word) != 0:
                    day_menu[day_menu.index(word)] += '\n'
            day_menu = ''.join(day_menu)
            self.weekly_menu.append(day_menu)


class CockpeatMenu:
    def __init__(self):
        self.menu_url = 'https://www.facebook.com/pg/COCKPEAT/posts'
        self.weekdays = [['poniedziałek', 'poniedzialek'], 'wtorek', ['środa', 'sroda'],
                         'czwartek', ['piątek', 'piatek']]
        self.day_of_the_week = datetime.today().weekday()
        self._get_page()
        self._decode_content()
        self._create_soup_object()
        self._get_posts_from_content()

    def get_todays_menu(self) -> dict:
        menu = ''
        if self.day_of_the_week < 5:
            if type(self.weekdays[self.day_of_the_week]) is list:
                for day in self.weekdays[self.day_of_the_week]:
                    menu = self._search_for_menu_by_day_name(day)
            else:
                return {'cockpeat_menu': self._search_for_menu_by_day_name(self.weekdays[self.day_of_the_week])}
        return {'cockpeat_menu': menu}

    def _get_page(self):
        self.page = requests.get(self.menu_url)

    def _decode_content(self):
        self.content = self.page.content.decode('utf-8', errors='ignore')

    def _create_soup_object(self):
        self.soup = BeautifulSoup(self.content, 'lxml')

    def _get_posts_from_content(self):
        self.posts = self.soup.find_all('div', class_='_427x')

    @staticmethod
    def _correct_text(text):
        re.sub(',[ ]*$', '', text)
        re.sub(',[ ]+', ', ', text)
        re.sub('[a-zA-Z]*(,)[a-zA-Z]*', ', ', text)
        return text.replace(' ,', ',')\
                   .replace(' :', ': ')\
                   .replace(' *', ' \n')\
                   .replace('  -', '\n  ')

    def _search_for_menu_by_day_name(self, day_name):
        todays_menu = ''
        for post in self.posts:
            if f"menu {day_name}" in post.text.lower() \
                    and ' o ' not in post.text.lower().split('menu')[0]:
                menu_entries = post.find_all('p')
                for menu_entry in menu_entries:
                    todays_menu += self._correct_text(menu_entry.text) + '\n'
                break
        return todays_menu


def get_all_menus() -> dict:
    list_of_classes = [AstraMenu, CockpeatMenu]
    all_menus = dict()
    for single_menu in map(lambda cls: cls().get_todays_menu(), list_of_classes):
        all_menus.update(single_menu)
    return all_menus


def check_if_all_menus_exist() -> bool:
    return '' not in get_all_menus().values()
