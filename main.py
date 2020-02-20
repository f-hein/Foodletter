# -*- coding: utf-8 -*-
import datetime
import logging
import os

from apscheduler.schedulers.blocking import BlockingScheduler

from bot_credentials import WL_USERNAME, WL_PASSWORD, GT_USERNAME, GT_PASSWORD
from sites import Wests, GreenTowers

logs_filepath = 'mail_logs.log'
logging.basicConfig(filename=logs_filepath, filemode='w', format='%(asctime)s %(message)s', level=logging.INFO)
# logging.getLogger('apscheduler').setLevel(logging.CRITICAL)

sites = [
    Wests(WL_USERNAME, WL_PASSWORD),
    GreenTowers(GT_USERNAME, GT_PASSWORD)
]


def run_foodletter():
    today = datetime.datetime.today().weekday()
    for site in sites:
        site.mail_checker.check_for_subscription_emails()
        if 0 <= today < 5 and not site.state.mails_were_sent_today() and site.all_menus_exist():
            email_object = site.mail_creator.create_email(None, msg_body=site.get_and_format_menus())
            list_of_emails = site.mailing_list.get_mails()
            for mail in list_of_emails:
                email_object['To'] = mail
                site.mail_sender.send_mail_to_one_recipient(mail, email_object)


if __name__ == '__main__':
    for site in sites:
        site.state.create_state_file()
    scheduler = BlockingScheduler()
    scheduler.add_job(run_foodletter, 'interval', minutes=1)
    print('Press Ctrl+{} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
