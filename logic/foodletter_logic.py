# -*- coding: utf-8 -*-
import datetime

from bot_credentials import WL_USERNAME, WL_PASSWORD, GT_USERNAME, GT_PASSWORD
from logic.sites import Wests, GreenTowers

sites = [
    Wests(WL_USERNAME, WL_PASSWORD),
    GreenTowers(GT_USERNAME, GT_PASSWORD)
    ]


def run_foodletter():
    today = datetime.datetime.today().weekday()
    for site in sites:
        site.subscription_checker.check()
        if 0 <= today < 5 and not site.state.mails_were_sent_today() and site.all_menus_exist():

            email_object = site.mail_creator.create_email(recipient=None, sender=site.email,
                                                          msg_body=site.get_and_format_menus())
            list_of_emails = site.mailing_list.get_mails()
            site.mail_sender.send_mail_to_many_recipients(list_of_emails, email_object)
            site.state.log_emails_were_sent()


def create_state_files():
    for site in sites:
        site.state.create_state_file()
