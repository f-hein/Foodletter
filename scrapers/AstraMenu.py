# -*- coding: utf-8 -*-
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from scrapers.IMenu import IMenu


class AstraMenu(IMenu):
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
        self.soup = BeautifulSoup(self.content, 'html.parser')

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
        text = re.sub(r'-\n', '\n', text)
        text = re.sub(r'[ ]{2,}', ' ', text)
        text = re.sub(r'\n{2,}', '\n', text)
        text = re.sub(r': \n', ': ', text)
        return text
