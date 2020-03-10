# -*- coding: utf-8 -*-
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from scrapers.IMenu import IMenu


class MeetingPointMenu(IMenu):
    def __init__(self):
        self.menu_url = 'https://www.meatingpoint.pl/lokal/robotnicza-42-wroclaw'
        self.day_of_the_week = datetime.today().weekday()
        self.daily_menu = ''
        self._get_contents_and_set_todays_menu()

    def get_todays_menu(self) -> dict:
        if self.day_of_the_week < 5:
            return {'meeting_point_menu': self.daily_menu}
        else:
            return {'meeting_point_menu': ''}

    def _get_contents_and_set_todays_menu(self):
        self._get_page()
        self._decode_content()
        self._create_soup_object()
        if self._validate_date():
            self._get_table_elements_from_content()
            self._get_soups_and_dishes()

    def _get_page(self):
        self.page = requests.get(self.menu_url, verify=False)

    def _decode_content(self):
        self.content = self.page.content.decode('utf-8', errors='ignore').replace('&oacute;', 'ó').replace('&nbsp;', '')

    def _create_soup_object(self):
        self.soup = BeautifulSoup(self.content, 'html.parser')

    def _validate_date(self):
        date_on_site = self.soup.findAll("div", {'class': 'theme-font day-menu-date'})[0].text
        if date_on_site.split()[0] == str(datetime.today().day):
            return True
        return False

    def _get_table_elements_from_content(self):
        self.table_elements = self.soup.find_all("div", {'class': 'col-md-6'})

    def _get_soups_and_dishes(self):
        soups_raw = self.table_elements[0].findAll('li')
        dishes_raw = self.table_elements[2].findAll('li')
        soups = [f"Zupa nr {index+1}: {value.text}" for index, value in enumerate(soups_raw)]
        dishes = [f"Danie dnia nr {index+1}: {value.text}" for index, value in enumerate(dishes_raw)]
        corrected_menu = self._correct_text('\n'.join(soups+dishes))
        self.daily_menu = corrected_menu

    @staticmethod
    def _correct_text(text):
        text = re.sub(r'^\s+', '', text)
        text = re.sub(r'\n[ ]+', '\n', text)
        text = re.sub(r'-\n', '\n', text)
        text = re.sub(r'[ ]{2,}', ' ', text)
        text = re.sub(r'\n{2,}', '\n', text)
        text = re.sub(r': \n', ': ', text)
        text = re.sub(r'\n$', '', text)
        text = re.sub(r'(?<=[a-zA-Z0-9]):(?=[a-zA-Z])', ': ', text)
        return text

print(MeetingPointMenu().get_todays_menu())
