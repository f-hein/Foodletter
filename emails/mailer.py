# -*- coding: utf-8 -*-
import imaplib
import logging
import re
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from emails.email_parts import footer, get_default_subject
from emails.mailing_list import MailingList


class MailCreator:
    def create_email(self, recipient: str, sender: str, subject=None, msg_body=None) -> MIMEMultipart:
        msg = MIMEMultipart()
        msg['From'] = f"FoodBot <{sender}>"
        msg['To'] = recipient
        msg['Subject'] = get_default_subject() if not subject else subject
        msg.attach(MIMEText(self._get_body_with_added_date_and_footer(msg_body), 'plain'))
        return msg

    @staticmethod
    def _get_body_with_added_date_and_footer(msg_body):
        return f'{date.today()}\n{msg_body}\n{footer}'


class MailSender:
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def send_mail_to_many_recipients(self, recipients: list, email_object: MIMEMultipart):
        for mail in recipients:
            email_object.replace_header("To", mail)
            self.send_mail_to_one_recipient(mail, email_object)

    def send_mail_to_one_recipient(self, recipient: str, email_object: MIMEMultipart):
        try:
            self._send_email(email_object)
            logging.info(f"Mail sent to {recipient}")
        except Exception as e:
            logging.error(f"Error while sending an email to: '{recipient}': {e}")

    def _send_email(self, email_object: MIMEMultipart) -> None:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(self.email, self.password)
        server.send_message(email_object)
        server.close()


class SubscriptionChecker:
    def __init__(self, email, password, site, send_confirmation_mails=True):
        self.email = email
        self.password = password
        self.site = site
        self.send_confirmation_mails = send_confirmation_mails
        self.imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        self.imap.login(email, password)
        self.imap.select('INBOX')

    def check(self) -> None:
        unread_mails_ids = self._get_unread_mails_ids()
        for email_id in unread_mails_ids:
            sender_email, subject, body = self._get_core_data_by_email_id(email_id)
            self._check_subscription_requests(sender_email, subject, body)

    @staticmethod
    def _get_sender_mail(body):
        return re.findall('<(.*)>', str(body[1][1]))[0]

    @staticmethod
    def _get_subject(body):
        return re.findall('(?<=Subject: )[a-zA-Z ]*', str(body[1][1]))[0].upper()

    def _check_subscription_requests(self, sender_email: str, subject: str, body: str):
        key_words = ['SUBSCRIBE', 'UNSUBSCRIBE']
        for key_word in key_words:
            if key_word in subject or key_word in body:
                MailingList(self.site).add(sender_email) if key_word == 'SUBSCRIBE' \
                    else MailingList(self.site).delete(sender_email)
                if self.send_confirmation_mails:
                    self._send_confirmation_email(key_word, sender_email)

    def _send_confirmation_email(self, subscribe_state, recipient):
        subject = f"{subscribe_state.lower()}d"
        body = f"You've been successfully {subscribe_state.lower()}d!"
        email_object = MailCreator().create_email(self.email, recipient, subject=subject, msg_body=body)
        MailSender(self.email, self.password).send_mail_to_one_recipient(recipient, email_object)

    def _get_unread_mails_ids(self):
        _, response = self.imap.search(None, '(UNSEEN)')
        return response[0].split()

    def _get_core_data_by_email_id(self, email_id):
        _, body = self.imap.fetch(email_id, '(BODY[TEXT] BODY[HEADER.FIELDS (FROM SUBJECT)])')
        sender_email = self._get_sender_mail(body)
        subject = self._get_subject(body)
        body = str(body[0][1]).upper()
        return sender_email, subject, body
