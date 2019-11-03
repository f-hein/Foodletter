# -*- coding: utf-8 -*-
from scrapers.AstraMenu import AstraMenu
from scrapers.CockpeatMenu import CockpeatMenu
from scrapers.ObiadeoMenu import ObiadeoMenu


def get_all_menus() -> dict:
    list_of_classes = [AstraMenu, CockpeatMenu, ObiadeoMenu]
    all_menus = dict()
    for single_menu in map(lambda cls: cls().get_todays_menu(), list_of_classes):
        all_menus.update(single_menu)
    return all_menus


def all_menus_exist() -> bool:
    return '' not in get_all_menus().values()
