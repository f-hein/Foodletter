# -*- coding: utf-8 -*-
import logging
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from emails.email_parts import footer, get_default_subject


class MailCreator:
    def create_email(self, recipient: str, sender: str, subject=None, msg_body=None,
                     use_mail_template=True) -> MIMEMultipart:
        msg = MIMEMultipart()
        msg['From'] = f"FoodBot <{sender}>"
        msg['To'] = recipient
        msg['Subject'] = get_default_subject() if not subject else subject
        if use_mail_template:
            msg.attach(MIMEText(self._get_body_with_added_date_and_footer(msg_body), 'plain'))
        else:
            msg.attach(MIMEText(msg_body, 'plain'))
        return msg

    @staticmethod
    def _get_body_with_added_date_and_footer(msg_body) -> str:
        return f'{date.today()}\n{msg_body}\n{footer}'


class MailSender:
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def send_mail_to_many_recipients(self, recipients: list, email_object: MIMEMultipart) -> None:
        for mail in recipients:
            email_object.replace_header("To", mail)
            self.send_mail_to_one_recipient(mail, email_object)

    def send_mail_to_one_recipient(self, recipient: str, email_object: MIMEMultipart) -> None:
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
