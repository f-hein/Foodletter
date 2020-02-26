from datetime import datetime

import requests
from bs4 import BeautifulSoup

from scrapers.IMenu import IMenu


class GreenTowersBistroMenu(IMenu):
    def __init__(self):
        self.menu_url = 'http://www.bistrogreentowers.pl/menu-tygodniowe'
        self.day_of_the_week = datetime.today().weekday()
        self.weekly_menu = list()
        self._get_page(self.day_of_the_week+1)
        self._decode_content()
        self._create_soup_object()
        self._get_tables_from_content()

    def get_todays_menu(self) -> dict:
        if self.day_of_the_week < 5:
            return {'green_towers_bistro_menu': self._get_menu()}
        else:
            return {'green_towers_bistro_menu': ''}

    def _get_page(self, day_of_the_week):
        self.page = requests.get(self.menu_url)

    def _decode_content(self):
        self.content = self.page.content.decode('utf-8', errors='ignore').replace('&oacute;', 'ó').replace('&nbsp;', '')

    def _create_soup_object(self):
        self.soup = BeautifulSoup(self.content, 'html.parser')

    def _get_tables_from_content(self):
        self.table = self.soup.find_all('table')[self.day_of_the_week]

    def _get_menu(self):
        tds = self.table.find_all("td")
        soup = "Zupa: {}".format(tds[1].text)
        featured_dishes = ["Danie dnia nr {}: {}".format(index+1, dishes) for index, dishes in
                           enumerate([x.text.replace("*", "") for x in tds if '*' in x.text])]
        featured_dishes = [soup] + featured_dishes
        return featured_dishes
