# -*- coding: utf-8 -*-
import re

from scrapers.FacebookPage import FacebookPage
from tools.levenshtein_distance import calc_levenshtein


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
            if re.findall('(?<=menu )[a-zA-ZŚąćęłńóśźż]+', text)[0]:
                return re.findall('(?<=menu )[a-zA-ZŚąćęłńóśźż]+', text)[0]
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
                        todays_menu += self._correct_text(self._format_p(menu_entry))
                break
        return todays_menu
