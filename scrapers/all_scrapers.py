# # -*- coding: utf-8 -*-
# import logging
#
# from scrapers.AstraMenu import AstraMenu
# from scrapers.CockpeatMenu import CockpeatMenu
# from scrapers.ObiadeoMenu import ObiadeoMenu
#
#
# def get_all_menus_wl() -> dict:
#     list_of_classes = [AstraMenu, CockpeatMenu, ObiadeoMenu]
#     all_menus = dict()
#     for single_menu in map(lambda cls: cls().get_todays_menu(), list_of_classes):
#         all_menus.update(single_menu)
#     return all_menus
#
#
# def get_all_menus_gt() -> dict:
#     list_of_classes = []
#     all_menus = dict()
#     for single_menu in map(lambda cls: cls().get_todays_menu(), list_of_classes):
#         all_menus.update(single_menu)
#     return all_menus


# def all_menus_exist() -> bool:
#     all_menus = get_all_menus()
#     if '' in all_menus.values():
#         for place_name, menu in all_menus.items():
#             if not menu:
#                 logging.info(f"{place_name} menu is still empty.")
#     return '' not in all_menus.values()
