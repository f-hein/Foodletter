# -*- coding: utf-8 -*-
import logging
import os

from apscheduler.schedulers.blocking import BlockingScheduler

from mailer import MailSender, MailChecker, MailingList, State
from scraper import all_menus_exist

logs_filepath = 'mail_logs.log'
logging.basicConfig(filename=logs_filepath, filemode='w', format='%(asctime)s %(message)s', level=logging.INFO)
logging.getLogger('apscheduler').setLevel(logging.CRITICAL)


def run_foodletter():
    MailChecker().check_for_subscription_emails()
    if not State().mails_were_sent_today() and all_menus_exist():
        list_of_emails = MailingList.get_mails()
        MailSender().send_email_to_many_recipients(list_of_emails)


if __name__ == '__main__':
    State().create_state_file()
    scheduler = BlockingScheduler()
    scheduler.add_job(run_foodletter, 'interval', minutes=1)
    print('Press Ctrl+{} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
