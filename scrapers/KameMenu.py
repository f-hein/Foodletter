# -*- coding: utf-8 -*-
import re
import datetime
from scrapers.FacebookPage import FacebookPage
from scrapers.IMenu import IMenu
from tools.levenshtein_distance import calc_levenshtein


class KameMenu(IMenu, FacebookPage):
    def __init__(self):
        super().__init__(fanpage_url='https://www.facebook.com/pg/kame.wro/posts')

    def get_todays_menu(self) -> dict:
        menu = ''
        if self.day_of_the_week < 5:
            menu = self._search_for_menu_by_day_name(self.weekdays[self.day_of_the_week])
        return {'kame_menu': menu}

    @staticmethod
    def _get_day_from_post(text):
        try:
            if re.findall('(?<=menu na )[a-zA-ZŚąćęłńóśźż]+', text)[0]:
                return re.findall('(?<=menu na )[a-zA-ZŚąćęłńóśźż]+', text)[0]
        except IndexError:
            return ''

    def _search_for_menu_by_day_name(self, day_name):
        todays_menu = ''
        for post in self.posts:
            day_in_post = self._get_day_from_post(post.text.lower())
            if day_in_post and calc_levenshtein(day_name, day_in_post) <= 2 \
                    and self._is_todays_date_in_post(post.text.lower()):
                menu_entries = post.find_all('p')
                for menu_entry in menu_entries:
                    todays_menu += self._correct_text(self._format_p(menu_entry))
                break
        return '\n'.join(todays_menu.split('\n')[1:])  # deleting the first line of memu (redundant)

    @staticmethod
    def _is_todays_date_in_post(post):
        d = datetime.date.today()
        todays_date = f"{d.day:02d}.{d.month:02d}"
        return todays_date in post
