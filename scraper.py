# -*- coding: utf-8 -*-
from datetime import datetime

import requests
import re
from bs4 import BeautifulSoup, NavigableString
from tools import calc_levenshtein
from abc import ABC, abstractmethod


class FacebookPage(ABC):
    def __init__(self, fanpage_url):
        self.fanpage_url = fanpage_url
        self.weekdays = ['poniedzialek', 'wtorek', 'sroda', 'czwartek', 'piatek']
        self.day_of_the_week = datetime.today().weekday()
        self._get_page()
        self._decode_content()
        self._create_soup_object()
        self._get_posts_from_content()

    def _get_page(self):
        self.page = requests.get(self.fanpage_url)

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
        return text.replace(' ,', ',') \
            .replace(' :', ': ') \
            .replace(' *', ' \n') \
            .replace('  -', '\n  ')

    @abstractmethod
    def get_todays_menu(self) -> dict:
        pass


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


class CockpeatMenu(FacebookPage):
    def __init__(self):
        super().__init__(fanpage_url='https://www.facebook.com/pg/COCKPEAT/posts')

    def get_todays_menu(self) -> dict:
        menu = ''
        if self.day_of_the_week < 5:
            menu = self._search_for_menu_by_day_name(self.weekdays[self.day_of_the_week])
        return {'cockpeat_menu': menu}

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


class ObiadeoMenu(FacebookPage):
    def __init__(self):
        super().__init__(fanpage_url='https://www.facebook.com/pg/obiadeo/posts')

    def get_todays_menu(self) -> dict:
        menu = ''
        if self.day_of_the_week < 5:
            menu = self._search_for_menu_by_day_name(self.weekdays[self.day_of_the_week])
        return {'obiadeo_menu': menu}

    @staticmethod
    def _get_days_with_dates_from_post(text):
        text = re.sub(r'[ ]{2,}', ' ', text)
        try:
            days_with_dates = re.findall('[a-zA-ZłśŁŚąę]{5,}[ ]+[0-9(.):]+', text)
            day_and_date_dict = dict()
            if len(days_with_dates) > 0:
                for day_and_date in days_with_dates:
                    if '...' not in day_and_date:
                        weekday, weekday_date = re.sub(r'[():]', '', day_and_date).split(" ")
                        if weekday not in day_and_date_dict:
                            day_and_date_dict[weekday] = weekday_date
                return day_and_date_dict
        except IndexError:
            return ''

    def _search_for_menu_by_day_name(self, searched_day_name):  # TODO: refactor this method
        todays_menu = ''
        for post in self.posts:
            days_with_dates = self._get_days_with_dates_from_post(post.text.lower())
            if days_with_dates:
                for day, day_date in days_with_dates.items():
                    if calc_levenshtein(day, searched_day_name) <= 2 and day_date.count('.') == 1:
                        now = datetime.now()
                        date_format = '%d.%m.%Y'
                        day_date_str = day_date + f'.{now.year}'
                        day_date_obj = datetime.strptime(day_date_str, date_format)
                        if day_date_obj.date() == now.date():  # if date and weekday are in post and is current day
                            menu_entries = post.find_all('p')
                            for menu_entry in menu_entries:
                                if day_date in menu_entry.text:
                                    temp_menu_list = [x for x in menu_entry.contents if type(x) is NavigableString][1:]
                                    todays_menu += '\n'.join(temp_menu_list).replace('<br/>', '\n')
                                    break
        return todays_menu


def get_all_menus() -> dict:
    list_of_classes = [AstraMenu, CockpeatMenu, ObiadeoMenu]
    all_menus = dict()
    for single_menu in map(lambda cls: cls().get_todays_menu(), list_of_classes):
        all_menus.update(single_menu)
    return all_menus


def all_menus_exist() -> bool:
    return '' not in get_all_menus().values()
