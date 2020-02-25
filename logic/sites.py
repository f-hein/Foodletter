import logging
from abc import ABC

from emails import SubscriptionChecker, MailSender, MailingList, MailCreator
from emails import State
from scrapers import AstraMenu, CockpeatMenu, ObiadeoMenu


class Site(ABC):
    def __init__(self, location_name, email, password, send_confirmation_mails=True):
        self.email = email
        self.password = password
        self.state = State(location_name)
        self.subscription_checker = SubscriptionChecker(email, password, location_name,
                                                        send_confirmation_mails=send_confirmation_mails)
        self.mail_creator = MailCreator()
        self.mail_sender = MailSender(email, password)
        self.mailing_list = MailingList(location_name)
        self.scrapers = list()

    def get_all_menus(self) -> dict:
        list_of_scrapers = self.scrapers
        all_menus = dict()
        for single_menu in map(lambda cls: cls().get_todays_menu(), list_of_scrapers):
            all_menus.update(single_menu)
        return all_menus

    def all_menus_exist(self) -> bool:
        all_menus = self.get_all_menus()
        if '' in all_menus.values():
            for place_name, menu in all_menus.items():
                if not menu:
                    logging.info(f"{place_name} menu is still empty.")
        return '' not in all_menus.values()

    def get_and_format_menus(self) -> str:
        formatted_mesage = ""
        template = "\n### {} ###\n{}"
        for place_name, menu in self.get_all_menus().items():
            formatted_mesage += template.format(place_name.replace("_", " ").upper(), menu)
        return formatted_mesage


class Wests(Site):
    def __init__(self, email, password, send_confirmation_mails=True):
        super().__init__('WL', email, password, send_confirmation_mails)
        self.scrapers = [AstraMenu, CockpeatMenu, ObiadeoMenu]


class GreenTowers(Site):
    def __init__(self, email, password, send_confirmation_mails=True):
        super().__init__('GT', email, password, send_confirmation_mails)
        self.scrapers = None

    def all_menus_exist(self):
        return False
