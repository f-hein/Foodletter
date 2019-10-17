# -*- coding: utf-8 -*-
from datetime import datetime

import requests
import re
from bs4 import BeautifulSoup
from tools import calc_levenshtein


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
            day_menu = self._correct_text(day_menu)
            self.weekly_menu.append(day_menu)

    @staticmethod
    def _correct_text(text):
        text = re.sub(r'^\s+', '', text)
        text = re.sub(r'\n[ ]+', '\n', text)
        text = re.sub(r'[ ]{2,}', ' ', text)
        return text


class CockpeatMenu:
    def __init__(self):
        self.menu_url = 'https://www.facebook.com/pg/COCKPEAT/posts'
        self.weekdays = ['poniedzialek', 'wtorek', 'sroda', 'czwartek', 'piatek']
        self.day_of_the_week = datetime.today().weekday()
        self._get_page()
        self._decode_content()
        self._create_soup_object()
        self._get_posts_from_content()

    def get_todays_menu(self) -> dict:
        menu = ''
        if self.day_of_the_week < 5:
            menu = self._search_for_menu_by_day_name(self.weekdays[self.day_of_the_week])
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
        text = re.sub(',[ ]*$', '', text)
        text = re.sub(',[ ]+', ', ', text)
        text = re.sub('[\W]*(,)[\W]*', ', ', text)
        text = re.sub(r'[ ]+', ' ', text)
        return text.replace(' ,', ',')\
                   .replace(' :', ': ')\
                   .replace(' *', ' \n')\
                   .replace('  -', '\n  ')

    @staticmethod
    def _get_day_from_post(text):
        text = re.sub(r'[ ]{2,}', ' ', text)
        try:
            if re.findall('(?<=menu )[a-ząćęłńóśźż]+', text)[0]:
                return re.findall('(?<=menu )[a-ząćęłńóśźż]+', text)[0]
        except IndexError:
            return ''

    def _search_for_menu_by_day_name(self, day_name):
        todays_menu = ''
        for post in self.posts:
            day_in_post = self._get_day_from_post(post.text.lower())
            if ' o ' not in post.text.lower().split('menu')[0] and day_in_post \
                    and calc_levenshtein(day_name, day_in_post) <= 2:  # issue: won't grab a post if there is 'wtorjek' at 'sroda'
                menu_entries = post.find_all('p')
                for menu_entry in menu_entries:
                    if menu_entries.index(menu_entry) > 0:  # cuts out the header "Menu ${weekday} from the post"
                        todays_menu += self._correct_text(menu_entry.text) + '\n'
                break
        return todays_menu


def get_all_menus() -> dict:
    list_of_classes = [AstraMenu, CockpeatMenu]
    all_menus = dict()
    for single_menu in map(lambda cls: cls().get_todays_menu(), list_of_classes):
        all_menus.update(single_menu)
    return all_menus


def all_menus_exist() -> bool:
    return '' not in get_all_menus().values()
