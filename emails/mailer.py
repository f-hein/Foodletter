# -*- coding: utf-8 -*-
import imaplib
import logging
import re
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bot_credentials import gmail_user, gmail_password
from emails.email_parts import footer, default_subject
from emails.mailing_list import MailingList
from emails.state import State
from scrapers.all_scrapers import all_menus_exist, get_all_menus


class MailSender:
    def send_email_to_many_recipients(self, recipients: list) -> None:
        if all_menus_exist():
            msg_body = self._create_email_body()
            for recipient in recipients:
                self.send_mail_to_one_recipient(recipient, msg_body=msg_body)
            State().log_todays_date()

    def send_mail_to_one_recipient(self, recipient: str, subject=None, msg_body=None):
        if subject:
            email_object = self._create_email(recipient, msg_body, subject)
        else:
            email_object = self._create_email(recipient, msg_body, default_subject)
        self._send_email(recipient, email_object)

    @staticmethod
    def _create_email(recipent: str, msg_body: str, subject: str) -> MIMEMultipart:
        msg = MIMEMultipart()
        msg['From'] = f"FoodBot <{gmail_user}>"
        msg['To'] = recipent
        msg['Subject'] = subject
        msg.attach(MIMEText(msg_body, 'plain'))
        return msg

    @staticmethod
    def _create_email_body(body=None) -> str:
        template = "\n### {} ###\n{}"
        formatted_mesage = f'{date.today()}\n'
        if body:
            return body + footer
        for place_name, menu in get_all_menus().items():
            formatted_mesage += template.format(place_name.replace("_", " ").upper(), menu)
        formatted_mesage += footer
        return formatted_mesage

    def _send_email(self, recipient: str, email_object: MIMEMultipart) -> None:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.send_message(email_object)
        logging.info(f"Mail sent to {recipient}")
        server.close()


class MailChecker:
    def __init__(self):
        self.imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        self.imap.login(gmail_user, gmail_password)
        self.imap.select('INBOX')

    def check_for_subscription_emails(self) -> None:
        _, response = self.imap.search(None, '(UNSEEN)')
        unread_mails_ids = response[0].split()
        for e_id in unread_mails_ids:
            _, body = self.imap.fetch(e_id, '(BODY[TEXT] BODY[HEADER.FIELDS (FROM SUBJECT)])')
            sender_email = re.findall('<(.*)>', str(body[1][1]))[0]
            subject = re.findall('(?<=Subject: )[a-zA-Z ]*', str(body[1][1]))[0].upper()
            body = str(body[0][1]).upper()
            if 'UNSUBSCRIBE' in body or 'UNSUBSCRIBE' in subject:
                MailingList.delete(sender_email)
                MailSender().send_mail_to_one_recipient(sender_email, subject="Unsubscribed",
                                                        msg_body="You've been successfully unsubscribed.")
            elif 'SUBSCRIBE' in body or 'SUBSCRIBE' in subject:
                MailingList.add(sender_email)
                MailSender().send_mail_to_one_recipient(sender_email, subject="Subscribed",
                                                        msg_body="You've been successfully subscribed!")
