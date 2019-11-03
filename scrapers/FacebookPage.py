# -*- coding: utf-8 -*-
import re
from abc import ABC, abstractmethod
from datetime import datetime

import requests
from bs4 import BeautifulSoup


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
