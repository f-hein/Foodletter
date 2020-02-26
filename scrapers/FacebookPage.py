# -*- coding: utf-8 -*-
import re
from abc import ABC, abstractmethod
from datetime import datetime

import requests
from bs4 import BeautifulSoup, NavigableString, Tag


class FacebookPage(ABC):
    def __init__(self, fanpage_url):
        self.fanpage_url = fanpage_url
        self.weekdays = ['poniedzialek', 'wtorek', 'sroda', 'czwartek', 'piatek']
        self.day_of_the_week = datetime.today().weekday()
        self._get_page()
        self._decode_content()
        self._create_soup_object()
        self.posts = self._get_posts_from_content()

    def _get_page(self):
        self.page = requests.get(self.fanpage_url)

    def _decode_content(self):
        self.content = self.page.content.decode('utf-8', errors='ignore')

    def _create_soup_object(self):
        self.soup = BeautifulSoup(self.content, 'html.parser')

    def _get_posts_from_content(self):
        return self.soup.find_all('div', class_='_427x')

    @staticmethod
    def _correct_text(text):
        text = re.sub(',[ ]*$', '', text)
        text = re.sub(',[ ]+', ', ', text)
        text = re.sub(r'[\W]*(,)[\W]*', ', ', text)
        text = re.sub('[ ]+', ' ', text)
        text = re.sub('(?<!\\n) --(?=[a-zA-Z]+)', '\n-', text)
        text = re.sub('\\n\(', ' (', text)
        text = re.sub('--', '-', text)
        text = re.sub('\.\.\.', '', text)
        text = re.sub('^[ ]+', '', text)
        text = re.sub('\\n \(', ' (', text)
        return text.replace(' ,', ',') \
            .replace(' :', ': ') \
            .replace(' *', ' \n') \
            .replace('  -', '\n  ') \
            .replace('\n ', '\n')

    @staticmethod
    def _format_p(entry_from_menu):
        formatted_entry = ''
        for elem in entry_from_menu.contents:
            if type(elem) is NavigableString:
                if elem.string:
                    formatted_entry += elem.string
            elif type(elem) is Tag:
                formatted_entry += elem.text if elem.text else '\n'
        formatted_entry += '\n'
        return formatted_entry
