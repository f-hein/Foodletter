# -*- coding: utf-8 -*-

import imaplib
import logging
import re
import smtplib
from datetime import date, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bot_credentials import gmail_user, gmail_password
from scraper import check_if_all_menus_exist, get_all_menus

subs_filepath = 'subscribers_list.txt'
state_filepath = 'logger_state.txt'


class MailSender:

    def send_email_to_many_recipients(self, recipients: list) -> None:
        if check_if_all_menus_exist():
            msg_body = self._get_email_body()
            for recipient in recipients:
                self._send_email(recipient, msg_body)
            self._log_action_to_file()

    @staticmethod
    def _create_email(recipent: str, message: str) -> MIMEMultipart:
        msg = MIMEMultipart()
        msg['From'] = f"FoodBot <{gmail_user}>"
        msg['To'] = recipent
        msg['Subject'] = f"[FOODBOT][{date.today()}] What's cooking? :)"
        msg.attach(MIMEText(message, 'plain'))
        return msg

    @staticmethod
    def _get_email_body() -> str:
        template = "\n### {} ###\n{}"
        formatted_mesage = f'{date.today()}\n'
        footer = "\n\nhttps://pajacyk.pl/ - Kliknij i pomóż dzieciom!\n"\
                 "\n----------\n" \
                 "Autor: Filip Hein <filip.hein@nokia.com>\n" \
                 "ABY ODSUBSKRYBOWAĆ LISTĘ MAILINGOWĄ WYŚLIJ MAIL O TREŚCI 'UNSUBSCRIBE' NA ADRES BOTA."
        for place_name, menu in get_all_menus().items():
            formatted_mesage += template.format(place_name.replace("_", " ").upper(), menu)
        formatted_mesage += footer
        return formatted_mesage

    def _send_email(self, recipient: str, message: str) -> None:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.send_message(self._create_email(recipient, message))
        logging.info(f"Mail sent to {recipient}")
        server.close()

    @staticmethod
    def _log_action_to_file() -> None:
        with open(state_filepath, 'w') as state_file:
            state_file.write(f"Last sent:\n{date.today()}")


class MailChecker:
    def __init__(self):
        self.imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        self.imap.login(gmail_user, gmail_password)
        self.imap.select('INBOX')

    def check_for_subscription_emails(self) -> None:
        _, response = self.imap.search(None, '(UNSEEN)')
        unread_mails_ids = response[0].split()
        for e_id in unread_mails_ids:
            _, body = self.imap.fetch(e_id, '(BODY[TEXT] BODY[HEADER.FIELDS (FROM)])')
            sender_email = re.findall('<(.*)>', str(body[1][1]))[0]
            if 'SUBSCRIBE' in body[1][1]:
                SubscriberList.add(sender_email)
            elif 'UNSUBSCRIBE' in body[1][1]:
                SubscriberList.delete(sender_email)


class SubscriberList:
    @staticmethod
    def add(email: str) -> None:
        with open(subs_filepath, 'a+') as subs_file:
            subs_file.seek(0)
            file_content = subs_file.read()
            if email not in file_content:
                subs_file.write(email+'\n')
                logging.info(f"Mail added to subscribers list: {email}")
            else:
                logging.error(f"Mail already added to subscribers list: {email}")

    @staticmethod
    def delete(email: str) -> None:
        with open(subs_filepath, 'r+') as subs_file:
            lines = subs_file.readlines()
            subs_file.seek(0)
            for line in lines:
                if email not in line:
                    subs_file.write(line)
                else:
                    logging.info(f"Mail deleted from subscribers list: {email}")
            subs_file.truncate()

    @staticmethod
    def get_mails() -> list:
        with open(subs_filepath, 'r') as subs_file:
            list_of_email_addresses = list(map(lambda x: x.rstrip(), subs_file.readlines()))
        return list_of_email_addresses


def check_if_last_mails_were_sent_today():
    with open(state_filepath, 'r') as state_file:
        last_sent_date = datetime.strptime(state_file.readlines()[1], "%Y-%m-%d").date()
    return last_sent_date == date.today()
