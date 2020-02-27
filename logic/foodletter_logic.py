# -*- coding: utf-8 -*-
import datetime

from logic.sites import Wests, GreenTowers


class FoodletterLogic:
    def __init__(self):
        self.sites = [Wests(), GreenTowers()]

    def run_foodletter(self):
        today = datetime.datetime.today().weekday()
        now = datetime.datetime.now()
        for site in self.sites:
            site.subscription_checker.check()
            if 0 <= today < 5 and not site.state.mails_were_sent_today() and site.all_menus_exist():
                if now.hour >= 9 and now.minute >= 15:  # just to be sure that GT doesn't send mails at 0:01
                    self._prepare_and_send_mails(site)
            elif 0 <= today < 5 and not site.state.mails_were_sent_today() and now.hour >= 10 and now.minute >= 30:
                self._prepare_and_send_mails(site)

    @staticmethod
    def _prepare_and_send_mails(site):
        email_object = site.mail_creator.create_email(recipient=None, sender=site.email,
                                                      msg_body=site.get_and_format_menus())
        list_of_emails = site.mailing_list.get_mails()
        site.mail_sender.send_mail_to_many_recipients(list_of_emails, email_object)
        site.state.log_emails_were_sent()
