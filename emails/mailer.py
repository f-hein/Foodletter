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
    def __init__(self, sender):
        self.sender = sender

    def create_email(self, recipient: str, subject=None, msg_body=None) -> MIMEMultipart:
        msg = MIMEMultipart()
        msg['From'] = f"FoodBot <{self.sender}>"
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

    def send_mail_to_one_recipient(self, recipient: str, email_object: MIMEMultipart):
        try:
            self._send_email(email_object)
            logging.info(f"Mail sent to {recipient}")
        except Exception as e:
            logging.error(f"Exception caught! {e}")
            logging.error(f"Failed to send mail to: '{recipient}'")

    def _send_email(self, email_object: MIMEMultipart) -> None:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(self.email, self.password)
        server.send_message(email_object)
        server.close()


class MailChecker:
    def __init__(self, email, password, site, send_confirmation_mails=True):
        self.email = email
        self.password = password
        self.site = site
        self.send_confirmation_mails = send_confirmation_mails
        self.imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        self.imap.login(email, password)
        self.imap.select('INBOX')

    def check_for_subscription_emails(self) -> None:
        _, response = self.imap.search(None, '(UNSEEN)')
        unread_mails_ids = response[0].split()
        for e_id in unread_mails_ids:
            _, body = self.imap.fetch(e_id, '(BODY[TEXT] BODY[HEADER.FIELDS (FROM SUBJECT)])')
            sender_email = self._get_sender_mail(body)
            subject = self._get_subject(body)
            body = str(body[0][1]).upper()
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
                    confirmation_mail_subject = f"{key_word.lower()}d"
                    confirmation_mail_body = f"You've been successfully {key_word.lower()}d!"
                    email_object = MailCreator().create_email(self.email, sender_email,
                                                              subject=confirmation_mail_subject,
                                                              msg_body=confirmation_mail_body)
                    MailSender(self.email, self.password).send_mail_to_one_recipient(sender_email, email_object)

    def _rebuild_subscribers_list(self):
        self.check_for_subscription_emails()
