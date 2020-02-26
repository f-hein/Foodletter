# -*- coding: utf-8 -*-
import re
from datetime import datetime

from bs4 import NavigableString

from scrapers.FacebookPage import FacebookPage
from scrapers.IMenu import IMenu
from tools.levenshtein_distance import calc_levenshtein


class ObiadeoMenu(IMenu, FacebookPage):
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
